"""
Claude Platform 101: Lesson 5b - Structured tool results

https://academy.claude.com/courses/claude-platform-101/what-is-tool-use

WHAT'S NEW (vs lesson 5)
  - Tool results are JSON instead of free text. Claude can read structured
    data more reliably, and your code can produce it from real APIs as is.

UNCHANGED
  - Tools are JSON schemas, 2 tools, and we write the loop ourselves.

Tool results are stubbed (hardcoded). The log_* calls come from log_helper.py
and only print what is happening; they are not part of the lesson.
"""

import asyncio
import json  # NEW: used to turn Python dicts into JSON strings
import anthropic
from models import CHEAPEST
from log_helper import (
    log_turn, log_model_request, log_model_response, log_model_usage,
    log_tool_request, log_tool_response, log_answer_to_user, Stopwatch,
)

client = anthropic.AsyncAnthropic()


# =============================================================================
# SECTION 1: TOOLS - what Claude is allowed to call
# =============================================================================
# The tools array tells Claude what's available:
# a name, a description, and a JSON schema for the inputs.
tools = [
    {
        "name": "get_weather",
        "description": "Get today's current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city to check"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_forecast",
        "description": "Get the weather forecast for the next few days for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city to check"},
            },
            "required": ["city"],
        },
    },
]


# =============================================================================
# SECTION 2: TOOL EXECUTION - what happens when Claude asks for a tool
# =============================================================================
# run_tool is just a hardcoded lookup. NEW: it returns JSON instead of plain text.
# Claude gets no schema for this JSON (tool definitions only describe inputs);
# it simply reads the string we send back, like any other text.
async def run_tool(name, tool_input):
    if name == "get_weather":
        result = {"city": tool_input["city"], "temp_f": 95, "conditions": "sunny"}  # stubbed
        return json.dumps(result)
    if name == "get_forecast":
        result = {  # stubbed
            "city": tool_input["city"],
            "days": [
                {"day": "Tue", "high_f": 95},
                {"day": "Wed", "high_f": 85},
                {"day": "Thu", "high_f": 75},
            ],
        }
        return json.dumps(result)
    raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# SECTION 3: AGENT LOOP - the conversation with Claude
# =============================================================================
# Each iteration sends the messages to Claude and switches on the stop reason.
async def main():
    model = CHEAPEST
    max_tokens = 1024
    # Try these too and watch which tools Claude picks:
    #   "What should I wear in Austin today?"     -> get_weather only
    #   "What should I wear in Austin tomorrow?"  -> get_forecast only
    question = "What should I wear in Austin today and tomorrow?"
    messages = [{"role": "user", "content": question}]

    turn = 0
    while True:
        turn += 1
        log_turn(turn)
        log_model_request(model=model, max_tokens=max_tokens, messages=messages, tools=tools)

        with Stopwatch() as sw:
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tools=tools,
                messages=messages,
            )

        log_model_response(response)
        log_model_usage(response, elapsed=sw.seconds)

        if response.stop_reason != "tool_use":
            # Claude is done ("end_turn"). Any other reason (e.g. "max_tokens")
            # also ends here, so we never loop forever on paid API calls.
            log_answer_to_user(response)
            break

        # stop_reason == "tool_use": find the tool_use blocks and run each one.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                log_tool_request(block.name, block.input)
                result = await run_tool(block.name, block.input)
                log_tool_response(block.name, result)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        # Push the assistant's response and our tool results back into messages,
        # then loop again so Claude can answer.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


asyncio.run(main())
