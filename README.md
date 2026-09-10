# CLI Coding Agent

This project is a very small Python-based CLI agent that talks to an OpenAI model, lets the model think in steps, and allows it to use a couple of controlled tools.

In simple words, we are building an agent that:

- takes a user query
- sends it to the model with a system prompt
- asks the model to respond in a fixed JSON format
- lets the model either plan, use a tool, or give the final answer
- repeats this until the model returns an `OUTPUT`

## What This Project Does

The main file is [cli_agent.py](E:/CLI-Coding-Agent/cli_agent.py).

It works like a loop:

1. The user gives a query.
2. The model returns a JSON step such as `PLAN`, `TOOL`, or `OUTPUT`.
3. If the model asks for a tool, Python runs that tool.
4. The tool result is sent back to the model as an `OBSERVE` step.
5. The loop continues until the model gives the final answer.

## Files

- [cli_agent.py](E:/CLI-Coding-Agent/cli_agent.py): the main agent loop
- [prompt.py](E:/CLI-Coding-Agent/prompt.py): the system prompt that tells the model how to behave
- [requirements.txt](E:/CLI-Coding-Agent/requirements.txt): Python dependencies

## Step Types

The agent uses a fixed step-based flow:

- `START`: the original user request
- `PLAN`: the model explains what it wants to do next
- `TOOL`: the model asks Python to run a tool
- `OBSERVE`: Python sends the tool result back to the model
- `OUTPUT`: the model gives the final answer

This makes the agent easier to control and easier to debug.

## Available Tools

Right now the agent supports two tools:

- `run_command`: runs a PowerShell command and returns the output
- `write_file`: creates or overwrites a file with given content

These are defined in [cli_agent.py](E:/CLI-Coding-Agent/cli_agent.py).

## How Input Works Right Now

At the bottom of [cli_agent.py](E:/CLI-Coding-Agent/cli_agent.py), the script currently asks for input directly:

```python
final_output = input("Enter your query: ")
final_output = run_agent(final_output, on_step=print)
```

That means when you run the file, it waits for you to type a query in the terminal.

You can also pass text directly to the function in code:

```python
result = run_agent("Create a hello world Python file", on_step=print)
print(result)
```

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

## Run

Use:

```powershell
python cli_agent.py
```

Then type your query when prompted.

## Current Flow In Simple Language

- Python starts the program.
- It loads the API key from `.env`.
- It sends your query plus the system prompt to the model.
- The model must answer in JSON.
- If the model wants a tool, Python runs it.
- Python sends the result back.
- The model continues until it gives the final answer.

## Notes

- The agent is designed for Windows PowerShell commands.
- File writing should happen through the `write_file` tool.
- The model output is validated using Pydantic before the step is accepted.


