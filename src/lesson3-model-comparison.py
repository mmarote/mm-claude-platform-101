"""
Claude Platform 101: Lesson 3 - Choosing the right model

You're shipping an app with Claude. Which model do you pick? If you default
to the smartest one, your API bill will surprise you. Pick the cheapest one,
and the output might not hold up. Each model has different trade-offs, and
picking the right one affects both quality and cost.

https://academy.claude.com/courses/claude-platform-101/choosing-the-right-model
"""

import asyncio
import anthropic
from models import ALL
from log_helper import log_model_request, log_answer_to_user, log_model_usage, Stopwatch


client = anthropic.AsyncAnthropic()

max_tokens = 2048
system_prompt = "You are a terse senior code reviewer. Give feedback in one paragraph."
user_prompt = """Review this code:
function add(a, b) {
  return a - b;
}
"""
messages = [{"role": "user", "content": f"{user_prompt}"}]


async def main():
    for model in ALL:

        log_model_request(model=model, max_tokens=max_tokens, system=system_prompt, messages=messages)

        with Stopwatch() as sw:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
            )

        log_model_usage(response, elapsed=sw.seconds)

        log_answer_to_user(response)


asyncio.run(main())