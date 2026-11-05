"""
Claude Platform 101: Lesson 5c - Decorated tools and the tool runner

https://academy.claude.com/courses/claude-platform-101/what-is-tool-use

WHAT'S NEW (vs lesson 5b)
  - Tools are Python functions with the @beta_async_tool decorator. The SDK
    builds the JSON schema for us from the type hints and the docstring.
  - The SDK tool runner owns the agent loop: no while loop, no stop_reason
    checks, no run_tool, no manually pushing tool results into messages.

UNCHANGED
  - 2 tools, JSON results, same question.

Tool results are stubbed (hardcoded). The log_* calls come from log_helper.py
and only print what is happening; they are not part of the lesson.
"""

import asyncio
import json
import anthropic
from anthropic import beta_async_tool  # NEW
from models import CHEAPEST
from log_helper import (
    log_turn, log_model_request, log_model_response, log_model_usage,
    log_tool_request, log_tool_response, log_answer_to_user,
)

client = anthropic.AsyncAnthropic()


# =============================================================================
# SECTION 1: TOOLS - what Claude is allowed to call
# =============================================================================
# NEW: a decorated function is a tool. Name = function name, description and
# parameter docs = docstring, parameter types = type hints.
# The tool body is also where the work happens (see SECTION 2).
@beta_async_tool
async def get_weather(city: str) -> str:
    """Get today's current weather for a city.

    Args:
        city: The city to check
    """
    log_tool_request("get_weather", {"city": city})
    result = json.dumps({"city": city, "temp_f": 95, "conditions": "sunny"})  # stubbed
    log_tool_response("get_weather", result)
    return result


@beta_async_tool
async def get_forecast(city: str) -> str:
    """Get the weather forecast for the next few days for a city.

    Args:
        city: The city to check
    """
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
# NEW: nothing to write here. The tool runner does exactly what run_tool did:
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

    # NEW: the tool runner replaces the while loop.
    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        tools=tools,
    )

    log_model_request(model=model, max_tokens=max_tokens, messages=messages, tools=tools)

    # Each item the runner yields is one response from Claude (one turn).
    turn = 0
    async for message in runner:
        turn += 1
        log_turn(turn)
        log_model_response(message)
        log_model_usage(message)

    log_answer_to_user(message)  # the last message is Claude's final answer


asyncio.run(main())
