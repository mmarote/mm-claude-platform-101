"""
Claude Platform 101: Lesson 5 - What is tool use?

Your existing workflows rely on a lot of different technologies — project
management software, databases, files. Claude can't just check these things
itself. Instead, it relies on tools, which give Claude access to external data
and actions.

https://academy.claude.com/courses/claude-platform-101/what-is-tool-use

Notes:
 1. Tool definitions are hardcoded in JSON - not a good practice.
 2. Tool responses are stubbed.
 3. Tool responses are unestructured text. Should be JSON.
 
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
    },
    {
        "name": "get_forecast",
        "description": "Get the weather forecast for the next few days for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to check",
                }
            },
            "required": ["city"],
        },
    }
]

# run_tool is just a hardcoded lookup.
# In a real app, this would hit your database, an API, whatever.
async def run_tool(name, tool_input):
    if name == "get_weather":
        # Hardcoded result. Unextructured text, use JSON for best practice.
        return f"Weather in {tool_input['city']}: 95F, sunny" 
    elif name == "get_forecast":
        # Hardcoded result. Unextructured text, use JSON for best practice.
        return f"Forecast in {tool_input['city']}: day 1: 95, sunny; day 2: 85, cloudy; day 3: 75: rain"
    raise ValueError(f"Unknown tool: {name}")

messages = [
    {"role": "user", "content": "What should I wear in Austin today and tomorrow?"}
    # {"role": "user", "content": "What should I wear in Austin today"}
    # {"role": "user", "content": "What should I wear in Austin tomorrow?"}
]

model = "claude-haiku-5-5"
max_tokens = 1024

# The agent loop. Each iteration sends messages to Claude
# and switches on the response's stop reason.
async def main():
    turn = 0
    while True:
        turn += 1

        print(f"\n{'=' * 60}\nTURN {turn}\n{'=' * 60}")
        print("-> REQUEST to Claude")
        print(f"   model:      {model}")
        print(f"   max_tokens: {max_tokens}")
        print(f"   tools:      {tools}")
        print(f"   messages:   {messages}")

        # Call Claude
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=tools,
            messages=messages,
        )
    
        print("-> RESPONSE from Claude")
        print(f"   stop_reason={response.stop_reason}")
        print(f"   response.content:\n" + "\n".join(b.model_dump_json(indent=4) for b in response.content))

        if response.stop_reason == "end_turn":
            # Claude is done. Print the final text and break.
            print("-> Claude is DONE. Printing final text. Ending agent.")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            # Find the tool use blocks in the response and run each one.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print("-> RUNNING tool")
                    result = await run_tool(block.name, block.input)
                    print(f"   tool call: {block.name}({block.input}) -> {result}")
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
