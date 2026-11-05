"""
Small logging helpers for the Claude Platform 101 lessons.

Seven functions, one per thing worth seeing:

    log_turn(...)             a header for each round trip with Claude
    log_model_request(...)    what we send to Claude
    log_model_response(...)   what Claude sends back (text and tool requests)
    log_model_usage(...)      tokens used by a call, and how long it took
    log_tool_request(...)     a tool call we are about to run
    log_tool_response(...)    what the tool returned
    log_answer_to_user(...)   Claude's final answer, the app's real output

Usage:
    from log_helper import (
        log_turn, log_model_request, log_model_response, log_model_usage,
        log_tool_request, log_tool_response, log_answer_to_user, Stopwatch,
    )

    log_turn(1)
    log_model_request(model=CHEAPEST, max_tokens=1024, messages=messages, tools=tools)
    with Stopwatch() as sw:
        response = await client.messages.create(...)
    log_model_response(response)
    log_model_usage(response, elapsed=sw.seconds)

    log_tool_request(block.name, block.input)
    result = await run_tool(block.name, block.input)
    log_tool_response(block.name, result)

    log_answer_to_user(response)    # when Claude is done

Turn the debug logs off with `log_helper.ENABLED = False`.
log_answer_to_user is not a debug log, so it always prints.
"""

import json
import time

ENABLED = True
MAX_CHARS = 1000  # long values are cut so the console stays readable


class Stopwatch:
    """Time a block of code: `with Stopwatch() as sw: ...` then read `sw.seconds`."""

    seconds = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc_info):
        self.seconds = time.perf_counter() - self._start


def _show(value, indent=2) -> str:
    """Turn almost anything (dicts, SDK objects, strings) into readable text.

    indent=None gives compact one-line JSON, used for short values like tool inputs.
    """
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, indent=indent, default=_to_jsonable)
        except TypeError:
            text = str(value)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + f"... [{len(text) - MAX_CHARS} more chars]"
    return text


def _to_jsonable(obj):
    """json.dumps fallback for SDK objects.

    Response objects are pydantic models; decorated tools (@beta_async_tool)
    know how to describe themselves as a tool schema with to_dict().
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump(exclude_none=True)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return str(obj)


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def log_turn(turn: int) -> None:
    """Print a header that separates one round trip with Claude from the next."""
    if not ENABLED:
        return
    print(f"\n{'=' * 60}\nTURN {turn}\n{'=' * 60}")


def log_model_request(*, model, max_tokens=None, messages=None, system=None, tools=None) -> None:
    """Log the request about to be sent to Claude."""
    if not ENABLED:
        return
    print("\n-> REQUEST to Claude")
    print(f"   model:      {model}")
    if max_tokens is not None:
        print(f"   max_tokens: {max_tokens}")
    if system:
        print(f"   system:     {_show(system)}")
    if tools:
        print("   tools:")
        print(_indent(_show(tools)))
    print("   messages:")
    print(_indent(_show(messages or [])))


def log_model_response(response) -> None:
    """Log Claude's response: stop reason, text and tool requests (see log_model_usage for tokens)."""
    if not ENABLED:
        return
    print("\n<- RESPONSE from Claude")
    print(f"   stop_reason: {response.stop_reason}")
    for block in response.content:
        if block.type == "text":
            print(f"   text:        {_show(block.text)}")
        elif block.type == "tool_use":
            print(f"   tool_use:    {block.name}({_show(block.input, indent=None)})  id={block.id}")
        else:
            print(f"   {block.type}:")
            print(_indent(_show(block)))


def log_model_usage(response, label=None, elapsed=None) -> None:
    """Log how many tokens a call used and, if given, how long it took.

    `label` replaces the model name in the header, which helps when you
    log several calls from the same model.
    `elapsed` is the call duration in seconds (see Stopwatch). The API
    response doesn't contain it, so the caller has to measure it.
    """
    if not ENABLED:
        return
    usage = getattr(response, "usage", None)
    title = label or getattr(response, "model", "?")
    if usage is None:
        print(f"\n$ USAGE {title}: not reported")
        if elapsed is not None:
            print(f"   time:          {elapsed:.2f}s")
        return
    print(f"\n$ USAGE {title}")
    print(f"   input_tokens:  {usage.input_tokens}")
    print(f"   output_tokens: {usage.output_tokens}")
    print(f"   total_tokens:  {usage.input_tokens + usage.output_tokens}")
    if elapsed is not None:
        speed = f" ({usage.output_tokens / elapsed:.0f} output tokens/s)" if elapsed > 0 else ""
        print(f"   time:          {elapsed:.2f}s{speed}")
    # Prompt-caching counters: only shown when the API reports them and they are not zero.
    for name in ("cache_read_input_tokens", "cache_creation_input_tokens"):
        count = getattr(usage, name, None)
        if count:
            print(f"   {name}: {count}")


def log_tool_request(name: str, tool_input) -> None:
    """Log a tool call right before we run it."""
    if not ENABLED:
        return
    print(f"\n-> RUNNING tool: {name}")
    print(f"   input:  {_show(tool_input, indent=None)}")


def log_tool_response(name: str, result) -> None:
    """Log what the tool returned, right after we run it."""
    if not ENABLED:
        return
    print(f"<- TOOL RESULT: {name}")
    print(f"   output: {_show(result, indent=None)}")


def log_answer_to_user(response) -> None:
    """Print Claude's final text answer for the user.

    Unlike the other helpers this ignores ENABLED: it is the program's
    output, not a debug log, so silencing the logs must not hide it.
    """
    text = "".join(block.text for block in response.content if block.type == "text")
    print(f"\n=== ANSWER TO USER ===\n{text}")
