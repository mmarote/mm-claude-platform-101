---
name: status-report-text
description: Turns a raw activity log into a short daily status report in our team's format. Use when asked for a status report or daily update.
---

# Status report generator

Write the report in exactly this format, and nothing else:

```
STATUS REPORT - <date from the log, or "today">

TL;DR: <one sentence, max 20 words>

DONE
- <item> (<owner>)

IN PROGRESS
- <item> (<owner>) - <percent or next step>

BLOCKED
- <item> (<owner>) - waiting on <what>
```

Rules:
- Group every log entry under exactly one heading. Write "- none" for an empty heading.
- One line per item. No paragraphs, no extra headings.
- Keep the owner's first name only.
