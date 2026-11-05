"""A small web UI to run the lesson scripts with a click.

Start it from the project root:   streamlit run runner-ui/app.py

It only READS the scripts in ../src and runs them as subprocesses, the same
way you would in a terminal. It never changes them.
"""

import ast
import os
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

# Extra warnings shown next to a lesson (matched on the file name prefix).
WARNINGS = {
    "lesson3": "Calls three models, including Opus. This is the most expensive lesson.",
    "lesson7c": "Creates a temporary folder with the memory files (path printed at the end).",
    "lesson8": "Uploads a new skill to your Anthropic account on every run.",
}

st.set_page_config(page_title="Claude Platform 101 - Runner", layout="wide")

# Hide the Deploy button and the three-dots menu in the top right corner.
st.markdown(
    """
    <style>
    [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)


def discover():
    """{folder name: [script paths]}, found by scanning src/*/lesson*.py."""
    groups = {}
    for folder in sorted(p for p in SRC.iterdir() if p.is_dir() and not p.name.startswith("__")):
        scripts = sorted(folder.glob("lesson*.py"))
        if scripts:
            groups[folder.name] = scripts
    return groups


def description(path):
    """The title and first paragraph of the script's docstring."""
    doc = ast.get_docstring(ast.parse(path.read_text())) or ""
    title, _, rest = doc.partition("\n")
    first = rest.strip().split("\n\n")[0].replace("\n", " ")
    return title, first


ANSWER_MARKER = "=== ANSWER TO USER ==="
BANNER = "=" * 60   # log_banner and log_turn lines
# Every other line that log_helper starts a new log entry with. An answer ends at any of them.
LOG_STARTS = ("-> REQUEST", "<- RESPONSE", "$ USAGE", "-> RUNNING", "<- TOOL RESULT")


def split_output(output):
    """Cut the output into [("log", text), ("answer", text), ...], in the order printed.

    An answer starts at the marker that log_answer_to_user prints and ends at the
    next banner line or log entry (or at the end of the output).
    """
    segments, buffer, in_answer = [], [], False

    def flush():
        text = "\n".join(buffer).strip("\n")
        if text.strip():
            segments.append(("answer" if in_answer else "log", text.strip() if in_answer else text))
        buffer.clear()

    for line in output.splitlines():
        if line.strip() == ANSWER_MARKER:
            flush()
            in_answer = True
        elif in_answer and (line.strip() == BANNER or line.startswith(LOG_STARTS)):
            flush()
            in_answer = False
            buffer.append(line)
        else:
            buffer.append(line)
    flush()
    return segments


def show(box, output):
    """Draw the output in order: log text in grey boxes, Claude's answers in green boxes."""
    segments = split_output(output)
    answers = sum(1 for kind, _ in segments if kind == "answer")
    seen = 0
    with box.container():
        for kind, text in segments:
            if kind == "answer":
                seen += 1
                label = "Answer to user" if answers == 1 else f"Answer to user ({seen} of {answers})"
                st.success(f"**{label}**\n\n{text}", icon="💬")
            else:
                st.code(text, language="text", wrap_lines=True)


def run(path, box):
    """Run a script, streaming its output as it arrives. Returns (output, exit code, seconds)."""
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONUNBUFFERED": "1"}
    start = time.perf_counter()
    proc = subprocess.Popen(
        [PYTHON, "-u", str(path)], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    output = ""
    for line in proc.stdout:
        output += line
        show(box, output)
    proc.wait()
    return output, proc.returncode, time.perf_counter() - start


groups = discover()
if not groups:
    st.error(f"No lesson scripts found in {SRC}")
    st.stop()

if "selected" not in st.session_state:
    st.session_state.selected = str(next(iter(groups.values()))[0])
if "results" not in st.session_state:
    st.session_state.results = {}
if "view" not in st.session_state:
    st.session_state.view = "Code"
if "run_requested" not in st.session_state:
    st.session_state.run_requested = False


def toggle_view():
    st.session_state.view = "Code" if st.session_state.view == "Output" else "Output"


def request_run():
    """Run button callback: show the Output view and run on the next rerun."""
    st.session_state.view = "Output"
    st.session_state.run_requested = True

# ---- Left: the scripts -------------------------------------------------------
with st.sidebar:
    st.title("Lessons")
    for folder, scripts in groups.items():
        with st.expander(folder, expanded=False):
            for script in scripts:
                is_selected = str(script) == st.session_state.selected
                if st.button(script.stem, key=str(script), use_container_width=True,
                             type="primary" if is_selected else "secondary"):
                    st.session_state.selected = str(script)
                    st.session_state.view = "Code"
                    st.rerun()

# ---- Right: the selected script ---------------------------------------------
script = Path(st.session_state.selected)
title, intro = description(script)
st.header(title or script.stem)
st.write(intro)

warning = next((text for prefix, text in WARNINGS.items() if script.name.startswith(prefix)), None)
if warning:
    st.warning(warning)

has_result = str(script) in st.session_state.results
side_by_side = st.session_state.get("side_by_side", False)
showing_output = st.session_state.view == "Output"

col_run, col_clear, col_view, col_side, _ = st.columns([1, 1, 2, 2, 3])
col_run.button("Run", type="primary", on_click=request_run)
if col_clear.button("Clear"):
    st.session_state.results.pop(str(script), None)
    st.session_state.view = "Code"
    st.rerun()
col_view.button(
    "Show code" if showing_output else "Show output",
    on_click=toggle_view,
    disabled=side_by_side or (not showing_output and not has_result),
)
col_side.toggle("Side by side", key="side_by_side")


def render_output(container):
    """Run the script if Run was pressed, then show its saved result in the container."""
    with container:
        box = st.empty()
        if st.session_state.run_requested:
            st.session_state.run_requested = False
            with st.spinner("Running..."):
                output, code, seconds = run(script, box)
            st.session_state.results[str(script)] = (output, code, seconds)
        result = st.session_state.results.get(str(script))
        if result:
            output, code, seconds = result
            show(box, output)
            (st.success if code == 0 else st.error)(f"Exit code {code} - {seconds:.1f}s")
        else:
            box.info("Press Run.")


if side_by_side:
    # Both panes scroll on their own, so a long lesson does not push the output off screen.
    left, right = st.columns(2)
    with left:
        st.code(script.read_text(), language="python", line_numbers=True, height=700)
    render_output(right.container(height=700))
elif showing_output:
    render_output(st.container())
else:
    st.code(script.read_text(), language="python", line_numbers=True)
