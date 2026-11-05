"""
Claude Platform 101: Lesson 7c - Built-in tools: memory (client side)

Lessons 7a and 7b used server tools: Anthropic ran them. Memory is a client
tool: Claude knows the tool (its schema is built in), but OUR code runs it.
Claude asks to view, create or edit files in a /memories folder, and the
SDK's ready-made helper does that on a folder we choose.

https://academy.claude.com/courses/claude-platform-101/built-in-tools

We run two separate conversations. The second one starts with an empty
message history, so the only way Claude can know the answer is by reading
what the first conversation saved in memory.

The log_* calls come from log_helper.py and only print what is happening;
they are not part of the lesson.
"""

import asyncio
import tempfile
from pathlib import Path
import anthropic
from anthropic.lib.tools._beta_builtin_memory_tool import BetaAsyncLocalFilesystemMemoryTool
from models import BALANCED
from log_helper import log_banner, log_turn, log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

model = BALANCED
max_tokens = 1024

# The helper that runs Claude's memory commands (view, create, str_replace, ...).
# Everything Claude saves goes into this folder, and nowhere else: the helper
# rejects paths that try to escape it. A temp folder keeps the demo harmless.
memory_folder = tempfile.mkdtemp(prefix="claude-memory-")
tools = [BetaAsyncLocalFilesystemMemoryTool(base_path=memory_folder)]


async def converse(question):
    """One conversation, with a fresh message history. Only the memory carries over."""
    messages = [{"role": "user", "content": question}]

    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        tools=tools,
    )

    log_model_request(model=model, max_tokens=max_tokens, tools=tools, messages=messages)

    turn = 0
    async for message in runner:    # the runner calls Claude and runs the memory commands
        turn += 1
        log_turn(turn)
        log_model_response(message)

    log_answer_to_user(message)


async def main():

    log_banner("CONVERSATION 1 - Claude saves something to memory")
    await converse("Remember that my favorite city is Austin.")

    log_banner("CONVERSATION 2 - new conversation, Claude reads its memory")
    await converse("What is my favorite city?")

    log_banner("WHAT IS IN THE MEMORY FOLDER")
    for file in sorted(Path(memory_folder).rglob("*")):
        if file.is_file():
            print(f"{file}:\n{file.read_text()}")


asyncio.run(main())
