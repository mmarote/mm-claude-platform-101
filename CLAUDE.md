# Project instructions

## Lesson files

- Lessons 4 to 5d (`src/lesson4-*` … `src/lesson5d-*`) are an incremental progression for a training session. Each file adds exactly one idea to the previous one; keep it that way.
- All of them share one layout: docstring with `WHAT'S NEW` / `UNCHANGED`, then `SECTION 1: TOOLS`, `SECTION 2: TOOL EXECUTION`, `SECTION 3: AGENT LOOP`. Mark anything new or changed vs the previous file with a `# NEW:` comment.
- Keep tool names, descriptions and the question identical across these files, so only the intended change shows up in a diff.
- Keep lessons simple and readable for students; teaching clarity beats clean architecture.
- Never hardcode a `claude-*` model ID; import from `src/models.py` (`CHEAPEST`, `ALL`).
- Use `src/log_helper.py` for logging request, response, usage and tool calls.
- Lesson scripts make paid API calls. Don't run them without asking; test with a mocked HTTP transport instead.

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
