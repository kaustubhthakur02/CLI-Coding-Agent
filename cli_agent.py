import json
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

from typing import Literal, Optional, Union

from prompt import SYSTEM_PROMPT
from pydantic import BaseModel, TypeAdapter, ValidationError
load_dotenv()

class ContentStep(BaseModel):
    step: Literal["START", "PLAN", "OUTPUT"]
    content: str


class ToolStep(BaseModel):
    step: Literal["TOOL"]
    tool: Literal["run_command", "write_file"]
    input: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None


AgentStep = Union[ContentStep, ToolStep]
agent_step_adapter = TypeAdapter(AgentStep)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_command(cmd: str):
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return {"exit_code": result.returncode, "output": output.strip()[:4000]}
    except Exception as e:
        return {"exit_code": 1, "output": f"Error running command: {e}"}


def write_file(path: str, content: str):
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content or "")
        return {"exit_code": 0, "output": f"Wrote {len(content or '')} bytes to {path}"}
    except Exception as e:
        return {"exit_code": 1, "output": f"Error writing file: {e}"}

def run_agent(query: str, model: str = "gpt-5.5", on_step=None) -> str:
    """Runs the START/PLAN/TOOL/OUTPUT loop for a single query and returns the final answer.

    If given, on_step(step_dict) is called for every PLAN/TOOL/OBSERVE/OUTPUT step,
    so callers (CLI, UI) can surface the agent's reasoning as it happens.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps({"step": "START", "content": query})},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=messages,
        )
        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})

        try:
            parsed = agent_step_adapter.validate_json(content)
        except ValidationError as e:
            observation = {"step": "OBSERVE", "content": f"Error: malformed step from model: {e}"}
            if on_step:
                on_step(observation)
            messages.append({"role": "user", "content": json.dumps(observation)})
            continue

        if on_step:
            on_step(parsed.model_dump())

        if parsed.step == "OUTPUT":
            return parsed.content

        if parsed.step == "TOOL":
            if parsed.tool == "run_command":
                result = run_command(parsed.input or "")
            elif parsed.tool == "write_file":
                result = write_file(parsed.path or "", parsed.content or "")
            else:
                result = {"exit_code": 1, "output": f"Error: unknown tool '{parsed.tool}'"}

            observation = {"step": "OBSERVE", "content": result}
            if on_step:
                on_step(observation)
            messages.append({"role": "user", "content": json.dumps(observation)})
            continue

        # nudge the model to continue — keeps last turn as "user"
        messages.append({"role": "user", "content": json.dumps({"step": "continue"})})


if __name__ == "__main__":
    input_query = input("Enter your query: ")
    final_output = run_agent(input_query, on_step=print)
    print(final_output)


