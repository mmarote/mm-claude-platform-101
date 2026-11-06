"""
Claude Platform 101: Lesson 12 - Your first managed agent

Until now, our code ran the agent loop: we sent a request, ran the tools and
sent the results back. A managed agent runs that loop on Anthropic's
infrastructure. We define the agent, give it an environment, start a session
and read the events it produces.

https://academy.claude.com/courses/claude-platform-101/building-your-first-managed-agent

The four building blocks:
  - Agent: model, system prompt and toolset. Reusable across sessions.
  - Environment: where the agent runs. Here, a cloud sandbox.
  - Session: one run of an agent in an environment. The unit of work.
  - Events: what goes in (user.message) and what comes out (agent.message,
    agent.tool_use, session.status_idle).

Managed agents are a beta feature. The SDK adds the beta header to these
calls, so you do not pass `betas=` here.

WHAT'S NEW
  - No tool schemas and no loop in our code. Anthropic runs the loop and the
    sandbox, and we read the event stream.

The sandbox can create files and run commands, so this demo runs the agent in
a limited-network environment.
"""

import asyncio
import anthropic
from models import CHEAPEST


client = anthropic.AsyncAnthropic()


async def main():

    # =============================================================================
    # 1. AGENT - model, system prompt and toolset. Create once, reuse many times.
    # =============================================================================
    # The bundled agent toolset gives the agent its own sandbox tools (shell,
    # file read/write, search). `default_config` turns them on.
    agent = await client.beta.agents.create(
        name="Line Counter",
        model=CHEAPEST,
        system="You are a helpful agent that completes small file tasks. Explain your plan and your actions.",
        tools=[{"type": "agent_toolset_20260401", "default_config": {"enabled": True}}],
    )
    print(f"Agent created: {agent.id}")

    # =============================================================================
    # 2. ENVIRONMENT - where the agent runs
    # =============================================================================
    # "cloud" means Anthropic hosts the sandbox. "limited" networking allows
    # no outside hosts unless you list them.
    environment = await client.beta.environments.create(
        name="line-counter-env",
        config={"type": "cloud", "networking": {"type": "limited"}},
    )
    print(f"Environment created: {environment.id}")

    # =============================================================================
    # 3. SESSION - one unit of work: this agent, in this environment
    # =============================================================================
    session = await client.beta.sessions.create(
        agent=agent.id,
        environment_id=environment.id,
        title="Count lines demo",
    )
    print(f"Session started: {session.id}")

    # =============================================================================
    # 4. OPEN THE STREAM FIRST, THEN SEND THE KICKOFF
    # =============================================================================
    # The stream only delivers events that happen after it opens. Open it
    # before sending the first message, or the first events are lost.
    stream = await client.beta.sessions.events.stream(session_id=session.id)
    try:
        await client.beta.sessions.events.send(
            session_id=session.id,
            events=[{
                "type": "user.message",
                "content": [{"type": "text", "text": "Make a temp file, count its lines, report back."}],
            }],
        )

        # =========================================================================
        # 5. READ THE EVENTS UNTIL THE AGENT STOPS
        # =========================================================================
        print("\n--- Events ---")
        async for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type == "agent.tool_use":
                print(f"\n[tool] {event.name}")
            elif event.type == "session.status_idle":
                # The agent is waiting. `end_turn` means it finished its work.
                # `requires_action` means it needs a reply from us, which this
                # demo does not send.
                print(f"\n--- Agent idle: {event.stop_reason.type} ---")
                break
    finally:
        await stream.close()


asyncio.run(main())
