# Claude Platform 101 – Practice Scripts

Practice scripts I wrote while following the **Claude Platform 101** course on [Anthropic Academy](https://academy.claude.com/courses/claude-platform-101). Each script in `src/` maps to one lesson, grouped in one folder per course section and is meant for learning and experimentation, not production use.

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

### How the tool lessons are organized

Lessons 4 to 5d are a progression: each file adds one idea to the previous one, so you can diff neighbouring files to see exactly what changed. They all share the same layout:

1. A docstring with **WHAT'S NEW** and **UNCHANGED** sections.
2. `SECTION 1: TOOLS` – how tools are defined.
3. `SECTION 2: TOOL EXECUTION` – how a tool call is run.
4. `SECTION 3: AGENT LOOP` – the conversation with Claude.

Anything added or changed compared with the previous file is marked with a `# NEW:` comment. The `log_*` calls come from [src/log_helper.py](src/log_helper.py); they only print what is happening and aren't part of the lessons.

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

Activate the virtual environment first (`source .venv/bin/activate`). The prompt should then start with `(.venv)`. Without it, `python` isn't found on macOS and the `anthropic` package isn't installed. In VS Code, `.vscode/settings.json` selects this environment, and the VS Code workspace file sets `PYTHONPATH` to `src` for terminals, so in a new VS Code terminal you can run `python src/<folder>/<script>.py` without the `PYTHONPATH=src` prefix.

Run any script from the project root. `PYTHONPATH=src` lets the scripts, which live in subfolders, import the shared [models.py](src/models.py) and [log_helper.py](src/log_helper.py):

```bash
PYTHONPATH=src python src/01-what-is-the-claude-platform/lesson2-first-api-call.py
PYTHONPATH=src python src/01-what-is-the-claude-platform/lesson3-choosing-the-right-model.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson4-the-agent-loop.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson5a-tool-use.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson5b-tool-use-json-results.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson5c-tool-runner.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson5d-tool-runner-with-metadata.py
PYTHONPATH=src python src/02-teaching-your-agent/lesson6-extended-thinking.py
PYTHONPATH=src python src/03-extending-your-agent/lesson7a-built-in-tools-server-side-web-search.py
PYTHONPATH=src python src/03-extending-your-agent/lesson7b-built-in-tools-server-side-code-execution.py
PYTHONPATH=src python src/03-extending-your-agent/lesson7c-built-in-tools-client-side-memory.py
PYTHONPATH=src python src/03-extending-your-agent/lesson8a-skills.py
PYTHONPATH=src python src/03-extending-your-agent/lesson8b-skills-with-scripts.py
```

On Windows (PowerShell), set the variable on its own line instead:

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python src/01-what-is-the-claude-platform/lesson2-first-api-call.py
```

Each call to the API is billed to your account. Lesson 3 calls three models, including Opus, so it costs the most.

## Runner UI (optional)

A small web app to run the lessons by clicking, instead of typing commands. It opens on a landing page with a card per course section. The lessons are listed on the left, grouped by section, and **Previous** / **Next** step through the course. Select a lesson to read its code, press **Run** to see the output, and use **Side by side** to show code and output together. Claude's final answers are highlighted in green boxes.

```bash
pip install -r runner-ui/requirements.txt   # once, with the virtual environment active
python run_ui.py
```

`python run_ui.py` is the same on macOS, Linux and Windows, and it finds the project's virtual environment by itself, so you do not need to activate it first. Extra arguments go to Streamlit, for example `python run_ui.py --server.port 8600`.

It only reads the scripts in `src/` and runs them as subprocesses, with the same `PYTHONPATH=src` as above, so it needs no changes to the lessons. Every Run calls the API, so it is billed to your account like running the script yourself. The code is in [runner-ui/app.py](runner-ui/app.py).

## Dependencies

Pinned in [requirements.txt](requirements.txt). The main ones are `anthropic` (the SDK) and `python-dotenv`. The optional runner UI has its own [runner-ui/requirements.txt](runner-ui/requirements.txt).
