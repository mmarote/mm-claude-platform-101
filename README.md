# Claude Platform 101 – Practice Scripts

Practice scripts I wrote while following the **Claude Platform 101** course on [Anthropic Academy](https://academy.claude.com/courses/claude-platform-101). Each script in `src/` maps to one lesson, grouped in one folder per course section and is meant for learning and experimentation, not production use. Some course lessons (1, 10, 11 and 13) have no Python code, so they have no script here. The runner UI shows them grayed out.

## Scripts

### `src/01-what-is-the-claude-platform/`

| Script | Lesson | What it demonstrates |
| --- | --- | --- |
| [lesson2-first-api-call.py](src/01-what-is-the-claude-platform/lesson2-first-api-call.py) | [Your first API call](https://academy.claude.com/courses/claude-platform-101/your-first-api-call) | Sends a buggy JavaScript snippet to Claude with a system prompt and prints the code review. |
| [lesson3-choosing-the-right-model.py](src/01-what-is-the-claude-platform/lesson3-choosing-the-right-model.py) | [Choosing the right model](https://academy.claude.com/courses/claude-platform-101/choosing-the-right-model) | Runs the same prompt against Haiku, Sonnet and Opus and prints each response with its token usage, to compare quality and cost. |

### `src/02-teaching-your-agent/`

| Script | Lesson | What it demonstrates |
| --- | --- | --- |
| [lesson4-the-agent-loop.py](src/02-teaching-your-agent/lesson4-the-agent-loop.py) | [The agent loop explained](https://academy.claude.com/courses/claude-platform-101/the-agent-loop-explained) | **Baseline.** A hand-written agent loop with one stubbed tool (`get_weather`), defined as a JSON schema, that switches on `stop_reason`. |
| [lesson5a-tool-use.py](src/02-teaching-your-agent/lesson5a-tool-use.py) | [What is tool use?](https://academy.claude.com/courses/claude-platform-101/what-is-tool-use) | **+ a second tool** (`get_forecast`). Claude now chooses which tools to call. |
| [lesson5b-tool-use-json-results.py](src/02-teaching-your-agent/lesson5b-tool-use-json-results.py) | same | **+ JSON tool results** instead of plain text. |
| [lesson5c-tool-runner.py](src/02-teaching-your-agent/lesson5c-tool-runner.py) | same | **+ `@beta_async_tool` decorators and the SDK tool runner.** No JSON schemas, no `run_tool`, no while loop. |
| [lesson5d-tool-runner-with-metadata.py](src/02-teaching-your-agent/lesson5d-tool-runner-with-metadata.py) | same | **+ explicit tool name/description and `Annotated[..., Field]`** parameter metadata. |
| [lesson6-extended-thinking.py](src/02-teaching-your-agent/lesson6-extended-thinking.py) | [What is thinking?](https://academy.claude.com/courses/claude-platform-101/what-is-thinking) | **+ extended thinking** (`thinking`, `output_config`), with token usage and time per turn. |

### `src/03-extending-your-agent/`

| Script | Lesson | What it demonstrates |
| --- | --- | --- |
| [lesson7a-built-in-tools-server-side-web-search.py](src/03-extending-your-agent/lesson7a-built-in-tools-server-side-web-search.py) | [Built-in tools](https://academy.claude.com/courses/claude-platform-101/built-in-tools) | The built-in **web search** server tool: declared with just a type and a name, run by Anthropic. Compares the basic and the newer (dynamic filtering) versions. |
| [lesson7b-built-in-tools-server-side-code-execution.py](src/03-extending-your-agent/lesson7b-built-in-tools-server-side-code-execution.py) | same | The built-in **code execution** server tool: Claude writes and runs Python in an Anthropic-hosted sandbox. |
| [lesson7c-built-in-tools-client-side-memory.py](src/03-extending-your-agent/lesson7c-built-in-tools-client-side-memory.py) | same | The built-in **memory** client tool. Two separate conversations: Claude saves a fact in the first and reads it back in the second. The SDK helper runs the commands on a temp folder, so it is safe. |
| [lesson8a-skills.py](src/03-extending-your-agent/lesson8a-skills.py) | [Skills](https://academy.claude.com/courses/claude-platform-101/skills) | Uploads a custom skill ([status-report-text](src/03-extending-your-agent/status-report-text/SKILL.md), instructions only) and attaches it to a request, so Claude writes a status report in our team's format. Each run uploads a new copy of the skill to your account. |
| [lesson8b-skills-with-scripts.py](src/03-extending-your-agent/lesson8b-skills-with-scripts.py) | same | **+ a script in the skill** ([status-report-with-script](src/03-extending-your-agent/status-report-with-script/SKILL.md)): Claude runs it to draw traffic lights and progress bars. Same request, only the skill folder changes. |
| [lesson9-mcp.py](src/03-extending-your-agent/lesson9-mcp.py) | [MCP](https://academy.claude.com/courses/claude-platform-101/mcp) | Connects to a public MCP server (DeepWiki, no account needed) with the **beta** MCP connector: `mcp_servers` plus an `mcp_toolset`. Call 1 allows all of the server's tools, call 2 allows only one. |

### `src/04-managed-agents/`

| Script | Lesson | What it demonstrates |
| --- | --- | --- |
| [lesson12-your-first-managed-agent.py](src/04-managed-agents/lesson12-your-first-managed-agent.py) | [Your first managed agent](https://academy.claude.com/courses/claude-platform-101/building-your-first-managed-agent) | A **managed agent** (beta): Anthropic runs the loop and a sandbox. We create an agent, an environment and a session, then read the event stream while the agent counts lines in a file. Each run creates a new agent, environment and session in your account, and they stay there. |

### How the tool lessons are organized

Lessons 4 to 5d each add one idea to the previous file, so you can diff neighbouring files to see what changed. Changes are marked with `# NEW:` comments, and the `log_*` calls come from [src/log_helper.py](src/log_helper.py) and aren't part of the lesson.

### Known simplifications

The tool-use scripts are intentionally simple:

- Tool results are stubbed (hardcoded). A real app would call an API or database.

## Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:

   ```
   ANTHROPIC_API_KEY=your-api-key
   ```

   `.env` is listed in `.gitignore`, so your key will not be committed.

   That's all you need. [src/models.py](src/models.py) calls `load_dotenv()`, and every script imports it, so the key is loaded automatically. If `ANTHROPIC_API_KEY` is already exported in your shell, that value takes priority over `.env`.

## Running

Activate the virtual environment, then run scripts from the project root. Scripts need `PYTHONPATH=src` so they can import the shared [models.py](src/models.py) and [log_helper.py](src/log_helper.py). Set it once per terminal:

- macOS/Linux: `export PYTHONPATH=src`
- Windows PowerShell: `$env:PYTHONPATH = "src"`

Then run any script with `python src/<folder>/<script>.py`. Each API call is billed to your account. Lesson 3 calls three models, including Opus, so it costs the most.

## Runner UI (optional)

A web app to run the lessons by clicking. Install once, then start it:

```bash
pip install -r runner-ui/requirements.txt
python run_ui.py
```

`run_ui.py` works the same on macOS, Linux and Windows, and finds the virtual environment itself. Every Run calls the API and is billed to your account. The code is in [runner-ui/app.py](runner-ui/app.py).

## Dependencies

Pinned in [requirements.txt](requirements.txt). The main ones are `anthropic` (the SDK) and `python-dotenv`. The optional runner UI has its own [runner-ui/requirements.txt](runner-ui/requirements.txt).
