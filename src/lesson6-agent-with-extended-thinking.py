"""
Claude Platform 101: Lesson 6 - Extended thinking

Some tasks need more than a quick answer. Claude can work through a problem
before responding — a feature called extended thinking. In this lesson, we'll
look at what thinking is, how it works, and when it actually helps.

https://academy.claude.com/courses/claude-platform-101/what-is-thinking

WHAT'S NEW (vs lesson 5d)
  - Extended thinking: Claude reasons before it answers (and between tool
    calls). We turn it on with thinking={"type": "adaptive", ...}, where
    "adaptive" lets Claude decide whether, and how much, to think.
  - "display": "summarized" returns the reasoning as a summary, in a `thinking`
    block next to the text and tool_use blocks, so we can read it.
    ("omitted" would hide the reasoning text.)
  - output_config={"effort": "high"} sets how much effort Claude puts in:
    low | medium | high | xhigh | max.
  - A much bigger max_tokens (16000). Thinking uses output tokens, and
    max_tokens limits them, so the limit must leave room for thinking and
    the answer.
  - A more open-ended question. Reasoning pays off on questions that need
    planning, not on simple lookups.

UNCHANGED
  - The same 2 tools (explicit metadata), JSON results, and the tool runner.

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
    log_turn, log_model_request, log_model_response, log_model_usage,
    log_tool_request, log_tool_response, log_answer_to_user, Stopwatch,
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
    # NEW: much higher limit. Thinking counts toward max_tokens (see the docstring).
    max_tokens = 16000
    # NEW: an open-ended question that gives Claude something to reason about.
    question = "Plan a road trip out of Austin with two stops, weighing weather and drive time."
    messages = [{"role": "user", "content": question}]

    # NEW: extended thinking. "adaptive" = Claude decides whether and how much to think.
    # "summarized" = return a summary of the reasoning, as a `thinking` block in each response.
    thinking = {"type": "adaptive", "display": "summarized"}
    # NEW: how much effort Claude puts in.
    output_config = {"effort": "high"}  # low | medium | high (default) | xhigh | max

    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        tools=tools,
        thinking=thinking,              # NEW
        output_config=output_config,    # NEW
    )

    log_model_request(
        model=model, max_tokens=max_tokens, messages=messages, tools=tools,
        thinking=thinking, output_config=output_config,
    )

    # The turns still happen, but the runner makes the calls to Claude itself
    # (and runs the tools in between). So we only log the first request, and
    # each turn's response as the runner yields it. Here it takes at least two
    # turns (the tool request, then the answer), and more if Claude asks for
    # tools again after seeing the first results. Each response can now also
    # contain a `thinking` block with the reasoning summary.
    note = "request not shown: the tool runner sent it, with the tool results"
    turn = 0

    # Thinking costs tokens (billed as output tokens) and time, so for this lesson
    # we also log the token usage and the time of every turn. sw.lap() is the
    # time since the previous turn: turn 1 is just the call to Claude, later
    # turns also include running the tools in between.
    with Stopwatch() as sw:
        # =====================================================================
        # CRITICAL LINE (same as lesson 5c): this loop is what runs the agent. Do not remove it.
        # Creating the runner above sends NOTHING to Claude. The runner only starts
        # working when we iterate over it. Each pass of this loop makes one call to
        # Claude, runs the tools it asks for, and hands us the response.
        # Without this line there are no API calls, no tool runs and no answer.
        # (The log_* lines inside the loop are optional. The loop itself is not.)
        # =====================================================================
        async for message in runner:    # <-- CRITICAL LINE
            turn += 1
            log_turn(turn, note=note if turn > 1 else None)
            log_model_response(message)
            log_model_usage(message, elapsed=sw.lap())

    log_answer_to_user(message)  # the last message is Claude's final answer


asyncio.run(main())
