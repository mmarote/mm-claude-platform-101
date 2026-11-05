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
# The virtual environment's Python: .venv/bin/python on macOS and Linux, .venv\\Scripts\\python.exe on Windows.
VENV_PYTHON = next(
    (p for p in (ROOT / ".venv" / "bin" / "python", ROOT / ".venv" / "Scripts" / "python.exe") if p.exists()),
    None,
)
PYTHON = str(VENV_PYTHON) if VENV_PYTHON else sys.executable

# Extra warnings shown next to a lesson (matched on the file name prefix).
WARNINGS = {
    "lesson3": "Calls three models, including Opus. This is the most expensive lesson.",
    "lesson7c": "Creates a temporary folder with the memory files (path printed at the end).",
    "lesson8": "Uploads a new skill to your Anthropic account on every run.",
}

COURSE_URL = "https://academy.claude.com/courses/claude-platform-101"

# Landing page text for each course section (matched on the folder name prefix).
SECTIONS = {
    "01": ("🚀", "What is the Claude Platform", "Make your first API call, then compare the Haiku, Sonnet and Opus models on the same prompt."),
    "02": ("🛠️", "Teaching your agent", "Build the agent loop by hand, add tools, move to the SDK tool runner, then let Claude think before it answers."),
    "03": ("🧩", "Extending your agent", "Use Anthropic's built-in tools (web search, code execution, memory) and teach Claude your way of working with skills."),
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
    doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
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
    # UTF-8 on both sides of the pipe: on Windows the default encoding cannot print the emoji and box characters.
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONUNBUFFERED": "1", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    start = time.perf_counter()
    proc = subprocess.Popen(
        [PYTHON, "-u", str(path)], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
        encoding="utf-8", errors="replace",
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
    st.session_state.selected = None   # None = the landing page
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

def open_lesson(path):
    st.session_state.selected = str(path)
    st.session_state.view = "Code"


def render_home():
    """The landing page: what this is, a link to the course, and one card per course section."""
    st.markdown(
        """
        <div style="padding: 3rem 2.5rem; border-radius: 18px; color: white;
                    background: linear-gradient(135deg, #c66240 0%, #d28267 45%, #15202b 100%);">
          <div style="font-size: 0.95rem; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.85;">
            Practice scripts for the course
          </div>
          <div style="font-size: 2.8rem; font-weight: 700; line-height: 1.15; margin: 0.4rem 0 0.8rem 0;">
            Claude Platform 101
          </div>
          <div style="font-size: 1.15rem; max-width: 46rem; opacity: 0.95;">
            Every lesson of the course as a small, runnable Python script. Read the code,
            press Run, and watch what the API sends and what Claude answers.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.link_button("Open the course on Anthropic Academy  ↗", COURSE_URL, type="primary")
    st.write("")

    st.subheader("Pick a section")
    columns = st.columns(len(groups))
    for column, (folder, scripts) in zip(columns, groups.items()):
        icon, title, text = SECTIONS.get(folder[:2], ("📘", folder, ""))
        with column.container(border=True):
            st.markdown(f"<div style='font-size: 2.6rem'>{icon}</div>", unsafe_allow_html=True)
            st.markdown(f"**{title}**")
            st.caption(f"{len(scripts)} lesson{'s' if len(scripts) != 1 else ''}")
            st.write(text)
            st.button("Start here", key=f"start-{folder}", on_click=open_lesson, args=(scripts[0],),
                      use_container_width=True)

    st.subheader("How it works")
    st.markdown(
        "1. Choose a lesson on the left.\n"
        "2. Read its code, then press **Run** to see the output. Claude's final answers appear in green boxes.\n"
        "3. Turn on **Side by side** to see the code and the output together.\n"
        "\n"
        "Every run calls the Anthropic API with your key, so it is billed like running the script yourself."
    )


# ---- Left: the scripts -------------------------------------------------------
with st.sidebar:
    st.title("Lessons")
    if st.button("🏠 Home", use_container_width=True,
                 type="primary" if st.session_state.selected is None else "secondary"):
        st.session_state.selected = None
        st.rerun()
    # The section of the selected lesson is open; the others are closed (all closed on Home).
    open_folder = Path(st.session_state.selected).parent.name if st.session_state.selected else None
    for folder, scripts in groups.items():
        with st.expander(folder, expanded=folder == open_folder):
            for script in scripts:
                is_selected = str(script) == st.session_state.selected
                if st.button(script.stem, key=str(script), use_container_width=True,
                             type="primary" if is_selected else "secondary"):
                    st.session_state.selected = str(script)
                    st.session_state.view = "Code"
                    st.rerun()

# ---- Right: the landing page, or the selected script ------------------------
if st.session_state.selected is None:
    render_home()
    st.stop()

script = Path(st.session_state.selected)
title, intro = description(script)

# Breadcrumb on the left, previous / next lesson on the right.
lessons = [path for scripts in groups.values() for path in scripts]
position = lessons.index(script)
section_title = SECTIONS.get(script.parent.name[:2], ("", script.parent.name, ""))[1]
crumb, previous_col, next_col = st.columns([6, 1.3, 1.3], vertical_alignment="center")
crumb.caption(f"{section_title}  ›  {script.stem}")
previous_col.button("← Previous", on_click=open_lesson, args=(lessons[max(position - 1, 0)],),
                    disabled=position == 0, use_container_width=True)
next_col.button("Next →", on_click=open_lesson, args=(lessons[min(position + 1, len(lessons) - 1)],),
                disabled=position == len(lessons) - 1, use_container_width=True)

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
        st.code(script.read_text(encoding="utf-8"), language="python", line_numbers=True, height=700)
    render_output(right.container(height=700))
elif showing_output:
    render_output(st.container())
else:
    st.code(script.read_text(encoding="utf-8"), language="python", line_numbers=True)
