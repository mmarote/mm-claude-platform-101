# Project instructions

## Lesson files

- Lesson scripts live in one folder per course section: `src/01-what-is-the-claude-platform/` (lessons 2-3), `src/02-teaching-your-agent/` (lessons 4-6) and `src/03-extending-your-agent/` (lesson 7). Shared helpers (`models.py`, `log_helper.py`) stay in `src/`.
- Scripts import the helpers with `from models import ...`, so run them from the project root with `PYTHONPATH=src python src/<folder>/<script>.py`.
- Lessons 4 to 5d (`src/02-teaching-your-agent/lesson4-*` … `lesson5d-*`) are an incremental progression for a training session. Each file adds exactly one idea to the previous one; keep it that way.
- All of them share one layout: docstring with `WHAT'S NEW` / `UNCHANGED`, then `SECTION 1: TOOLS`, `SECTION 2: TOOL EXECUTION`, `SECTION 3: AGENT LOOP`. Mark anything new or changed vs the previous file with a `# NEW:` comment.
- Keep tool names, descriptions and the question identical across these files, so only the intended change shows up in a diff.
- Lesson 6 builds on 5d. Lessons 2, 3 and 7a-7c are standalone: each teaches one thing and follows the lesson 2 style (docstring with the course link, `main()`, `create()` parameters as variables).
- Keep lessons simple and readable for students; teaching clarity beats clean architecture.
- Never hardcode a `claude-*` model ID; import from `src/models.py` (`CHEAPEST`, `BALANCED`, `MOST_CAPABLE`, `ALL`).
- Use `src/log_helper.py` for logging request, response, usage and tool calls.
- Lesson scripts make paid API calls. Don't run them without asking; test with a mocked HTTP transport instead.
- When files are renamed or moved, update the links and run commands in `README.md` in the same change.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org) for every commit message, both when suggesting one and when committing.

Format:

```
<type>(optional scope): <short description>

[optional body: what and why]

[optional footer: BREAKING CHANGE, issue refs]
```

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Description: imperative mood, lowercase, no trailing period, about 50 characters.
- Breaking changes: add `!` after the type (`feat!: ...`) or a `BREAKING CHANGE:` footer.
- One logical change per commit. Split unrelated changes into separate commits.
- Pick the type by what changed, e.g. `build` for `requirements.txt`, `docs` for README/CLAUDE.md, `refactor` for restructuring without behavior change.
- Example: `feat(models): add CHEAPEST/BALANCED/MOST_CAPABLE aliases`

Do not add a `Co-Authored-By` line (or any other attribution trailer) to commit messages.

Only commit when asked.
