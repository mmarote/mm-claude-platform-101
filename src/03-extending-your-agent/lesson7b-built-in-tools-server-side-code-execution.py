"""
Claude Platform 101: Lesson 7b - Built-in tools: code execution

Same idea as lesson 7a: declare the tool and Anthropic runs it. Here Claude
writes Python and runs it in a sandbox that Anthropic hosts, so it can do
real calculations instead of guessing.

https://academy.claude.com/courses/claude-platform-101/built-in-tools

The log_* calls come from log_helper.py and only print what is happening;
they are not part of the lesson.
"""

import asyncio
import anthropic
from models import BALANCED
from log_helper import log_banner, log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

model = BALANCED
max_tokens = 1024
# Again just a type and a name. Docs:
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool
tools = [{"type": "code_execution_20260120", "name": "code_execution"}]
# The prompt asks for code, otherwise Claude may just do the arithmetic in its head.
messages = [
    {"role": "user", "content": "Use code to calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"}
]


async def main():

    # The code Claude wrote and its output come back in this same response,
    # as `server_tool_use` and code execution result blocks. No agent loop.
    log_banner("CODE EXECUTION")

    log_model_request(model=model, max_tokens=max_tokens, tools=tools, messages=messages)

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        tools=tools,
        messages=messages,
    )

    log_model_response(response)
    log_answer_to_user(response)


asyncio.run(main())
