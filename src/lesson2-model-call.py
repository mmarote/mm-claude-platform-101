"""
Claude Platform 101: Lesson 2 - Your first API call

Saying hi to Claude might warm your heart, but it's not really useful.
In this lesson we'll send Claude something real and get structured insight
back — in just under 20 lines of code.

https://academy.claude.com/courses/claude-platform-101/your-first-api-call
"""

import asyncio
import anthropic
from models import CHEAPEST
from log_helper import log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

model = CHEAPEST
max_tokens = 1024
system_prompt = "You are a terse senior code reviewer. Give feedback in one paragraph."
user_prompt = """Review this code:
function add(a, b) {
  return a - b;
}
"""
messages = [{"role": "user", "content": f"{user_prompt}"}]


async def main():

    log_model_request(model=model, max_tokens=max_tokens, system=system_prompt, messages=messages)

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )

    log_model_response(response)

    for block in response.content:
        if block.type == "text":
            print(f"\n=== ANSWER TO USER ===\n{block.text}")


asyncio.run(main())
