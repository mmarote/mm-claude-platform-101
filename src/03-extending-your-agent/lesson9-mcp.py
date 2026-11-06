"""
Claude Platform 101: Lesson 9 - MCP

Custom tools are for your own stuff. MCP is for everyone else's stuff: the
service provider publishes and maintains an MCP server, and Claude discovers
its tools and schemas by itself. We write no schemas and no implementation.

https://academy.claude.com/courses/claude-platform-101/mcp

NOTE: The MCP connector is a BETA feature. That is why this lesson uses
client.beta.messages.create() and passes the `betas` parameter.

This lesson connects to DeepWiki's public MCP server, which needs no account
and no token. For a server that needs auth (Linear, Slack, ...), add an
`authorization_token` to the server definition.

The log_* calls come from log_helper.py and only print what is happening;
they are not part of the lesson.
"""

import asyncio
import anthropic
from models import BALANCED
from log_helper import log_banner, log_model_request, log_model_response, log_answer_to_user


client = anthropic.AsyncAnthropic()

model = BALANCED
max_tokens = 1024
betas = ["mcp-client-2025-11-20"]

# Where the MCP server lives. `name` is how we refer to it in `tools` below.
mcp_servers = [
    {
        "type": "url",
        "url": "https://mcp.deepwiki.com/mcp",
        "name": "deepwiki"
    },
]


async def main():

    # =============================================================================
    # CALL 1: ALL TOOLS - Claude discovers what the server offers
    # =============================================================================
    # `mcp_servers` declares the connection. `mcp_toolset` in `tools` gives
    # Claude access to that server's tools, by name. By default ALL of them
    # are available. Anthropic connects to the server and runs the tool calls;
    # the results come back in this same response as `mcp_tool_use` and
    # `mcp_tool_result` blocks, so no agent loop is needed.
    log_banner("MCP - all tools of the server")

    tools = [{"type": "mcp_toolset", "mcp_server_name": "deepwiki"}]
    messages = [
        # {"role": "user", "content": "Use the deepwiki server to tell me what the anthropics/anthropic-sdk-python repository is about. Answer in two sentences."}
        {"role": "user", "content": "What tools do you have available?"}
    ]

    log_model_request(model=model, max_tokens=max_tokens, betas=betas, mcp_servers=mcp_servers, tools=tools, messages=messages)

    response = await client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        betas=betas,
        mcp_servers=mcp_servers,
        tools=tools,
        messages=messages,
    )

    log_model_response(response)
    log_answer_to_user(response)
    print("")


    # =============================================================================
    # CALL 2: FILTERED TOOLS - allow only some of the tools
    # =============================================================================
    # To restrict access, disable every tool by default, then enable the ones
    # you want. Useful for read-only access, and to keep tool definitions from
    # using up context. Here Claude can ask a question, but cannot read the wiki
    # structure first: the log shows only ask_wiki_question being called.
    log_banner("MCP - only ask_wiki_question enabled")

    tools = [
        {
            "type": "mcp_toolset",
            "mcp_server_name": "deepwiki",
            "default_config": {"enabled": False},
            "configs": {"ask_wiki_question": {"enabled": True}},
        }
    ]

    log_model_request(model=model, max_tokens=max_tokens, betas=betas, mcp_servers=mcp_servers, tools=tools, messages=messages)

    response = await client.beta.messages.create(
        model=model,
        max_tokens=max_tokens,
        betas=betas,
        mcp_servers=mcp_servers,
        tools=tools,
        messages=messages,
    )

    log_model_response(response)
    log_answer_to_user(response)


asyncio.run(main())
