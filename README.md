# Claude Platform 101 – Practice Scripts

Practice scripts I wrote while following the **Claude Platform 101** course on [Anthropic Academy](https://academy.claude.com/courses/claude-platform-101). Each script in `src/` maps to one lesson and is meant for learning and experimentation, not production use.

## Scripts

| Script | Lesson | What it demonstrates |
| --- | --- | --- |
| [lesson2-model-call.py](src/lesson2-model-call.py) | [Your first API call](https://academy.claude.com/courses/claude-platform-101/your-first-api-call) | Sends a buggy JavaScript snippet to Claude with a system prompt and prints the code review. |
| [lesson3-model-comparison.py](src/lesson3-model-comparison.py) | [Choosing the right model](https://academy.claude.com/courses/claude-platform-101/choosing-the-right-model) | Runs the same prompt against Haiku, Sonnet and Opus and prints each response with its token usage, to compare quality and cost. |
| [lesson4-agent-with-1-stubbed-tool.py](src/lesson4-agent-with-1-stubbed-tool.py) | [The agent loop explained](https://academy.claude.com/courses/claude-platform-101/the-agent-loop-explained) | **Baseline.** A hand-written agent loop with one stubbed tool (`get_weather`), defined as a JSON schema, that switches on `stop_reason`. |
| [lesson5-agent-with-2-stubbed-tools.py](src/lesson5-agent-with-2-stubbed-tools.py) | [What is tool use?](https://academy.claude.com/courses/claude-platform-101/what-is-tool-use) | **+ a second tool** (`get_forecast`). Claude now chooses which tools to call. |
| [lesson5b-agent-with-json-tool-results.py](src/lesson5b-agent-with-json-tool-results.py) | same | **+ JSON tool results** instead of plain text. |
| [lesson5c-agent-with-tool-runner.py](src/lesson5c-agent-with-tool-runner.py) | same | **+ `@beta_async_tool` decorators and the SDK tool runner.** No JSON schemas, no `run_tool`, no while loop. |
| [lesson5d-agent-with-tool-metadata.py](src/lesson5d-agent-with-tool-metadata.py) | same | **+ explicit tool name/description and `Annotated[..., Field]`** parameter metadata. |

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
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root:

   ```
   ANTHROPIC_API_KEY=your-api-key
   ```

   `.env` is listed in `.gitignore`, so your key will not be committed.

   That's all you need. [src/models.py](src/models.py) calls `load_dotenv()`, and every script imports it, so the key is loaded automatically. If `ANTHROPIC_API_KEY` is already exported in your shell, that value takes priority over `.env`.

## Running

Run any script from the project root:

```bash
python src/lesson2-model-call.py
python src/lesson3-model-comparison.py
python src/lesson4-agent-with-1-stubbed-tool.py
python src/lesson5-agent-with-2-stubbed-tools.py
python src/lesson5b-agent-with-json-tool-results.py
python src/lesson5c-agent-with-tool-runner.py
python src/lesson5d-agent-with-tool-metadata.py
```

Each call to the API is billed to your account. Lesson 3 calls three models, including Opus, so it costs the most.

## Dependencies

Pinned in [requirements.txt](requirements.txt). The main ones are `anthropic` (the SDK) and `python-dotenv`.
