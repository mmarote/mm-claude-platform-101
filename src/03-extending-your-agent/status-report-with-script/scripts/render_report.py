"""Render a status report with traffic lights and progress bars.

Usage: echo '<json>' | python render_report.py

Input JSON:
  {"date": "Tue 5 Nov", "tldr": "one sentence",
   "items": [{"title": "...", "owner": "Maria",
              "status": "done" | "in_progress" | "blocked",
              "percent": 0-100,            (in_progress only)
              "waiting_on": "..."}]}      (blocked only)
"""

import json
import sys

LIGHT = {"done": "🟢", "in_progress": "🟡", "blocked": "🔴"}
HEADING = {"done": "DONE", "in_progress": "IN PROGRESS", "blocked": "BLOCKED"}
WIDTH = 10


def bar(percent):
    filled = round(WIDTH * percent / 100)
    return "▓" * filled + "░" * (WIDTH - filled) + f" {percent:>3}%"


def render(report):
    items = report["items"]
    total = len(items)
    done = sum(1 for i in items if i["status"] == "done")
    lines = [
        "╔" + "═" * 46 + "╗",
        "║" + f"  STATUS REPORT - {report.get('date', 'today')}".ljust(46) + "║",
        "╚" + "═" * 46 + "╝",
        "",
        f"TL;DR: {report['tldr']}",
        "",
        "Overall  " + bar(round(100 * done / total) if total else 0) + f"  ({done}/{total} done)",
    ]
    for status in ("done", "in_progress", "blocked"):
        group = [i for i in items if i["status"] == status]
        lines += ["", f"{LIGHT[status]} {HEADING[status]}"]
        if not group:
            lines.append("   - none")
        for i in group:
            line = f"   - {i['title']} ({i['owner']})"
            if status == "in_progress":
                line += "\n     " + bar(i.get("percent", 0))
            elif status == "blocked":
                line += f" - waiting on {i.get('waiting_on', '?')}"
            lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(json.load(sys.stdin)))
