"""
Claude Platform 101: Lesson 4 - The agent loop explained

You've made API calls, but a single call only returns one response.
If you want to automate a workflow, Claude needs to act, look at the result,
decide what's next, and keep going. That pattern is what people mean when they
talk about agentic workflows.

https://academy.claude.com/courses/claude-platform-101/the-agent-loop-explained

NOTE: These are custom tools, not MCP. We write and maintain the schemas and
the implementation. With MCP, the service provider publishes the tools for you.

THIS LESSON
  - 1 tool (get_weather), defined as a JSON schema
  - Tool results are plain text
  - We write the agent loop ourselves: a while loop that switches on stop_reason

Tool results are stubbed (hardcoded). In a real app they would come from an
API or a database. The log_* calls come from log_helper.py and only print
what is happening; they are not part of the lesson.
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
# The tools array tells Claude what's available: a name, a description, and
# a JSON schema for the inputs. Claude only knows about these tools because
# we pass the array to the API call in SECTION 3 (client.messages.create(tools=tools)).
#
# Note there is no schema for the OUTPUT. A tool definition only describes what
# Claude sends in. What comes back is whatever our code returns in a tool_result
# (SECTION 2), and Claude reads it as text. The API doesn't check its shape.
# If Claude needs to know what to expect, say so in the description.
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
]


# =============================================================================
# SECTION 2: TOOL EXECUTION - what happens when Claude asks for a tool
# =============================================================================
# run_tool is called by OUR code, never by Claude. When Claude wants a tool it
# replies with stop_reason == "tool_use" and a tool_use block that tells us:
#   block.name   which tool to run         e.g. "get_weather"
#   block.input  the arguments, shaped by the input_schema, with values Claude
#                picked from the conversation   e.g. {"city": "Austin"}
#   block.id     a label to send back with the result
# The loop in SECTION 3 passes name and input to this function.
# This one is just a hardcoded lookup, and it returns plain text.
async def run_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['city']}: 95F, sunny"  # stubbed
    raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# SECTION 3: AGENT LOOP - the conversation with Claude
# =============================================================================
# Each iteration sends the messages to Claude and switches on the stop reason.
async def main():
    model = CHEAPEST
    max_tokens = 1024
    question = "What should I wear in Austin today?"  # only one tool, so only "today"
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
