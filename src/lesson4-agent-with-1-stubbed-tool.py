"""
Claude Platform 101: Lesson 4 - The agent loop explained

You've made API calls, but a single call only returns one response.
If you want to automate a workflow, Claude needs to act, look at the result,
decide what's next, and keep going. That pattern is what people mean when they
talk about agentic workflows.

https://academy.claude.com/courses/claude-platform-101/the-agent-loop-explained
"""

import asyncio
import anthropic

client = anthropic.AsyncAnthropic()

# The tools array tells Claude what's available:
# a name, a description, and a JSON schema for the inputs.
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for",
                }
            },
            "required": ["city"],
        },
    }
]

messages = [
    {"role": "user", "content": "What should I wear in Austin today?"}
]


# run_tool is just a hardcoded lookup.
# In a real app, this would hit your database, an API, whatever.
async def run_tool(name, tool_input):
    if name == "get_weather":
        return f"Weather in {tool_input['city']}: 95F, sunny"   # Hardcoded result.
    raise ValueError(f"Unknown tool: {name}")


# The agent loop. Each iteration sends messages to Claude
# and switches on the response's stop reason.
async def main():
    turn = 0
    while True:
        turn += 1
        response = await client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )
        print(f"--- Turn {turn}: stop_reason={response.stop_reason}")

        if response.stop_reason == "end_turn":
            # Claude is done. Print the final text and break.
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            # Find the tool use blocks in the response and run each one.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await run_tool(block.name, block.input)
                    print(f"    tool call: {block.name}({block.input}) -> {result}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Push the assistant's response and our tool results
            # back into messages, then loop again so Claude can answer.
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})


asyncio.run(main())
