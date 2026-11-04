"""
Claude Platform 101: Lesson 2 - Your first API call

Saying hi to Claude might warm your heart, but it's not really useful.
In this lesson we'll send Claude something real and get structured insight
back — in just under 20 lines of code.

https://academy.claude.com/courses/claude-platform-101/your-first-api-call
"""

import asyncio
import anthropic

client = anthropic.AsyncAnthropic()

buggy_code = """
function add(a, b) {
  return a - b;
}
"""

MODEL = "claude-haiku-5-5"  # Cheapest as of Nov 2026
SYSTEM_PROMPT = "You are a terse senior code reviewer. Give feedback in one paragraph."
USER_PROMPT = f"Review this code:\n{buggy_code}"

async def main():
    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT},
        ],
    )

    for block in response.content:
        if block.type == "text":
            print(block.text)


asyncio.run(main())
