---
name: status-report-with-script
description: Turns a raw activity log into a daily status report with traffic lights and progress bars, in our team's format. Use when asked for a status report or daily update.
---

# Status report generator

Do NOT write the report yourself. A script in this skill draws it.

1. Read the activity log and sort every entry into one item:
   - `done`: finished work
   - `in_progress`: started but not finished (give `percent`; estimate 10 if the log gives none)
   - `blocked`: waiting on someone or something (give `waiting_on`)
2. Build this JSON, with the owner's first name only and a TL;DR of at most 20 words:

   ```json
   {"date": "<date from the log, or today's date>", "tldr": "...",
    "items": [{"title": "...", "owner": "Maria", "status": "done"},
              {"title": "...", "owner": "Joao", "status": "in_progress", "percent": 60},
              {"title": "...", "owner": "Priya", "status": "blocked", "waiting_on": "legal approval"}]}
   ```

3. Run `scripts/render_report.py` (it is in this skill's folder) with that JSON on stdin.
4. Reply with the script's output exactly as printed, inside a code block, and nothing else.
