"""
Claude Platform 101: Lesson 5d - Explicit tool metadata

https://academy.claude.com/courses/claude-platform-101/what-is-tool-use

WHAT'S NEW (vs lesson 5c)
  - Tool name and description are passed to the decorator instead of being
    taken from the function name and docstring.
  - Parameter descriptions use Annotated[..., Field(...)] instead of the
    docstring, so each parameter's schema lives next to its type.

UNCHANGED
  - 2 tools, JSON results, the tool runner, same question.

Tool results are stubbed (hardcoded). The log_* calls come from log_helper.py
and only print what is happening; they are not part of the lesson.
"""

import asyncio
import json
from typing import Annotated  # NEW
import anthropic
from anthropic import beta_async_tool
from pydantic import Field  # NEW
from models import CHEAPEST
from log_helper import (
    log_turn, log_model_request, log_model_response,
    log_tool_request, log_tool_response, log_answer_to_user,
)

client = anthropic.AsyncAnthropic()


# =============================================================================
# SECTION 1: TOOLS - what Claude is allowed to call
# =============================================================================
# NEW: name and description are explicit, and the parameter is described with
# Annotated + Field. No docstring is needed for the schema.
# The function body is the tool's implementation: it is what runs when Claude
# asks for this tool, so definition and implementation live together.
@beta_async_tool(
    name="get_weather",
    description="Get today's current weather for a city.",
)
async def get_weather(
    city: Annotated[str, Field(description="The city to check")],
) -> str:
    log_tool_request("get_weather", {"city": city})
    result = json.dumps({"city": city, "temp_f": 95, "conditions": "sunny"})  # stubbed
    log_tool_response("get_weather", result)
    return result


@beta_async_tool(
    name="get_forecast",
    description="Get the weather forecast for the next few days for a city.",
)
async def get_forecast(
    city: Annotated[str, Field(description="The city to check")],
) -> str:
    log_tool_request("get_forecast", {"city": city})
    result = json.dumps(  # stubbed
        {
            "city": city,
            "days": [
                {"day": "Tue", "high_f": 95},
                {"day": "Wed", "high_f": 85},
                {"day": "Thu", "high_f": 75},
            ],
        }
    )
    log_tool_response("get_forecast", result)
    return result


tools = [get_weather, get_forecast]


# =============================================================================
# SECTION 2: TOOL EXECUTION - what happens when Claude asks for a tool
# =============================================================================
# Nothing to write here. The tool runner does exactly what run_tool did:
# it reads name and input from Claude's tool_use block, calls the matching
# decorated function, and sends the result back to Claude.


# =============================================================================
# SECTION 3: AGENT LOOP - the conversation with Claude
# =============================================================================
async def main():
    model = CHEAPEST
    max_tokens = 1024
    # Try these too and watch which tools Claude picks:
    #   "What should I wear in Austin today?"     -> get_weather only
    #   "What should I wear in Austin tomorrow?"  -> get_forecast only
    question = "What should I wear in Austin today and tomorrow?"
    messages = [{"role": "user", "content": question}]

    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        tools=tools,
    )

    log_model_request(model=model, max_tokens=max_tokens, messages=messages, tools=tools)

    # The turns still happen, but the runner makes the calls to Claude itself
    # (and runs the tools in between). So we only log the first request, and
    # each turn's response as the runner yields it. With tools that is two turns:
    # the tool request, then the answer.
    note = "request not shown: the tool runner sent it, with the tool results"
    turn = 0

    # =========================================================================
    # CRITICAL LINE (same as lesson 5c): this loop is what runs the agent. Do not remove it.
    # Creating the runner above sends NOTHING to Claude. The runner only starts
    # working when we iterate over it. Each pass of this loop makes one call to
    # Claude, runs the tools it asks for, and hands us the response.
    # Without this line there are no API calls, no tool runs and no answer.
    # (The log_* lines inside the loop are optional. The loop itself is not.)
    # =========================================================================
    async for message in runner:    # <-- CRITICAL LINE
        turn += 1
        log_turn(turn, note=note if turn > 1 else None)
        log_model_response(message)

    log_answer_to_user(message)  # the last message is Claude's final answer


asyncio.run(main())
