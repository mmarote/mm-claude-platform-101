"""
Claude Platform 101: Lesson 7a - Built-in tools: web search

You can build your own custom tools, but some capabilities are common enough
that Anthropic ships them pre-built. You don't write the code. You don't host
anything. You just declare the tool, and Anthropic runs it.

https://academy.claude.com/courses/claude-platform-101/built-in-tools

This lesson runs the same question twice, with two versions of the web search
tool, so you can compare how they behave.

The log_* calls come from log_helper.py and only print what is happening;
they are not part of the lesson.
"""

import asyncio
import anthropic
from models import CHEAPEST, BALANCED
from log_helper import log_banner, log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

max_tokens = 1024
messages = [
    {"role": "user", "content": "What is Anthropic's latest model release? Answer in one sentence."}
]


async def main():

    # =============================================================================
    # CALL 1: BASIC WEB SEARCH - Claude calls the tool directly
    # =============================================================================
    # A built-in tool is just a type and a name. No description, no parameters
    # and no function body: the schema is built into Claude, and Anthropic runs
    # the search on its own servers.
    # No agent loop is needed either. The search result comes back in this same
    # response, as `server_tool_use` and `web_search_tool_result` blocks.
    # The version is part of the type. Versions are listed here:
    # https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
    log_banner("WEB SEARCH - basic (web_search_20250305)")

    model = CHEAPEST
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    log_model_request(model=model, max_tokens=max_tokens, tools=tools, messages=messages)

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        tools=tools,
        messages=messages,
    )

    log_model_response(response)
    log_answer_to_user(response)
    print("")


    # =============================================================================
    # CALL 2: NEWER WEB SEARCH - Claude calls it from code (dynamic filtering)
    # =============================================================================
    # Same question, same pattern, newer version. Now Claude writes Python that
    # calls web_search and filters the results before reading them. We did not
    # declare code execution, but the response will contain `code_execution`
    # blocks anyway: Claude is using it behind the scenes to filter the results.
    # This version needs a stronger model: Haiku sent malformed tool input.
    log_banner("WEB SEARCH - newer (web_search_20260209)")

    model = BALANCED
    tools = [{"type": "web_search_20260209", "name": "web_search"}]

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
