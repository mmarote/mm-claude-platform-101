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

client = anthropic.AsyncAnthropic()

buggy_code = """
function add(a, b) {
  return a - b;
}
"""

SYSTEM_PROMPT = "You are a terse senior code reviewer. Give feedback in one paragraph."
USER_PROMPT = f"Review this code:\n{buggy_code}"

models = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]

async def main():
    for model in models:
        response = await client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": USER_PROMPT},
            ],
        )
        print("")
        print(model)
        print(f"USAGE: {response.usage}")

        for block in response.content:
            if block.type == "text":
                print(f"RESPONSE: {block.text}")


asyncio.run(main())