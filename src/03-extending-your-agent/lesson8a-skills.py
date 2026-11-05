"""
Claude Platform 101: Lesson 8a - Skills

Tools are about WHAT Claude can do. Skills are about HOW you want it done.
A skill is a folder of instructions (a SKILL.md file, plus optional scripts and
resources) that Claude loads when it is relevant. Only the skill's name and
description are loaded up front; the full instructions are loaded when needed.

https://academy.claude.com/courses/claude-platform-101/skills

Two steps:
  1. Upload the skill once (client.skills.create). We get back an ID.
  2. Attach it to a request, in the `container` parameter. Skills run inside
     the code execution container, so the code execution tool must be enabled.

Our skill is in ./status-report-text/SKILL.md. It only contains instructions:
it teaches Claude our team's status report format. Read it first: the prompt
below never describes the format, yet the answer should follow it.

Note: every run uploads a new copy of the skill to your account. You can
delete the extra copies later in the Claude Console.

The log_* calls come from log_helper.py and only print what is happening;
they are not part of the lesson.
"""

import asyncio
from pathlib import Path
import anthropic
from anthropic.lib import async_files_from_dir
from models import BALANCED
from log_helper import log_banner, log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

model = BALANCED
max_tokens = 4096
skill_folder = Path(__file__).parent / "status-report-text"   # contains SKILL.md

activity_log = """\
09:10 Freda merged the login page redesign.
10:30 Joao started the database migration, about 60% done.
11:45 Priya is waiting on legal approval to publish the privacy policy.
14:00 Joao fixed the checkout bug reported on Monday.
15:20 Freda began work on the settings page, just started.
"""

# Skills run in the code execution container, so this tool is required.
tools = [{"type": "code_execution_20250825", "name": "code_execution"}]


async def main():

    # =============================================================================
    # STEP 1: UPLOAD THE SKILL - once. The response has the ID we use below.
    # =============================================================================
    log_banner("UPLOAD THE SKILL")

    skill = await client.skills.create(
        display_name="Status Report (text)",
        files=await async_files_from_dir(skill_folder),
    )
    print(f"skill id: {skill.id}")

    # =============================================================================
    # STEP 2: ATTACH THE SKILL TO A REQUEST - in `container`. Several can be listed.
    # =============================================================================
    log_banner("ASK FOR A STATUS REPORT")

    container = {"skills": [{"type": "custom", "skill_id": skill.id, "version": "latest"}]}
    messages = [
        {"role": "user", "content": f"Generate the daily status report from this activity log:\n\n{activity_log}"}
    ]

    log_model_request(model=model, max_tokens=max_tokens, container=container, tools=tools, messages=messages)

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        container=container,
        tools=tools,
        messages=messages,
    )

    log_model_response(response)
    log_answer_to_user(response)


asyncio.run(main())
