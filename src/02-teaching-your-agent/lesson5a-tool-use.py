"""
Claude Platform 101: Lesson 5a - What is tool use?

Your existing workflows rely on a lot of different technologies — project
management software, databases, files. Claude can't just check these things
itself. Instead, it relies on tools, which give Claude access to external data
and actions.

https://academy.claude.com/courses/claude-platform-101/what-is-tool-use

NOTE: These are custom tools, not MCP. We write and maintain the schemas and
the implementation. With MCP, the service provider publishes the tools for you.

WHAT'S NEW (vs lesson 4)
  - A second tool (get_forecast). Claude now chooses which tool(s) to call.
  - A question that needs both tools.

UNCHANGED
  - Tools are JSON schemas, results are plain text, we write the loop ourselves.

Tool results are stubbed (hardcoded). The log_* calls come from log_helper.py
and only print what is happening; they are not part of the lesson.
"""

import asyncio
import anthropic
from models import CHEAPEST
from log_helper import (
    log_turn, log_model_request, log_model_response,
    log_tool_request, log_tool_response, log_answer_to_user,
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
    # NEW: a second tool
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
# run_tool is just a hardcoded lookup, and it returns plain text.
async def run_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['city']}: 95F, sunny"  # stubbed
    # NEW: run the second tool
    if name == "get_forecast":
        return f"Forecast in {tool_input['city']}: day 1: 95, sunny; day 2: 85, cloudy; day 3: 75, rain"  # stubbed
    raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# SECTION 3: AGENT LOOP - the conversation with Claude
# =============================================================================
# Each iteration sends the messages to Claude and switches on the stop reason.
async def main():
    model = CHEAPEST
    max_tokens = 1024
    # NEW: a question that needs both tools. Try these too and watch which tools Claude picks:
    #   "What should I wear in Austin today?"     -> get_weather only
    #   "What should I wear in Austin tomorrow?"  -> get_forecast only
    question = "What should I wear in Austin today and tomorrow?"
    messages = [{"role": "user", "content": question}]

    turn = 0
    while True:
        turn += 1
        log_turn(turn)
        log_model_request(model=model, max_tokens=max_tokens, messages=messages, tools=tools)

        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=tools,
            messages=messages,
        )

        log_model_response(response)

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
