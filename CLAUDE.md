# Project instructions

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
