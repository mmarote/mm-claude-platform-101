"""A small web UI to run the lesson scripts with a click.

Start it from the project root:   streamlit run runner-ui/app.py

It only READS the scripts in ../src and runs them as subprocesses, the same
way you would in a terminal. It never changes them.
"""

import ast
import base64
import difflib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
# The virtual environment's Python: .venv/bin/python on macOS and Linux, .venv\Scripts\python.exe on Windows.
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
# The Claude logo (transparent PNG) for the "Open the course" box, embedded as a data URI.
LOGO_BASE64 = base64.b64encode((ROOT / "runner-ui" / "assets" / "claude-logo.png").read_bytes()).decode()

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


@st.cache_data
def _parse_docstring(path_str, modified):
    """The title and first paragraph of a script's docstring (cached until the file changes)."""
    doc = ast.get_docstring(ast.parse(Path(path_str).read_text(encoding="utf-8"))) or ""
    title, _, rest = doc.partition("\n")
    first = rest.strip().split("\n\n")[0].replace("\n", " ")
    return title, first


def description(path):
    return _parse_docstring(str(path), path.stat().st_mtime)


def course_lesson_url(path):
    """The course page for this lesson, taken from the link in its docstring (None if there is none)."""
    match = re.search(r"https://academy\.claude\.com/courses/claude-platform-101/[\w-]+", path.read_text(encoding="utf-8"))
    return match.group(0) if match else None


def lesson_label(path):
    """A friendly name for a lesson, e.g. '5b · Structured tool results', with a check mark once it has run."""
    title, _ = description(path)
    match = re.search(r"Lesson (\w+) - (.*)", title)
    label = f"{match.group(1)} · {match.group(2)}" if match else path.stem
    return ("✓ " if str(path) in st.session_state.get("results", {}) else "") + label


# Lessons that come in several examples (5a-5d, 7a-7c, 8a-8b) are shown as ONE lesson with a row of examples.
LESSON_NAMES = {"5": "Tool use", "7": "Built-in tools", "8": "Skills"}
# Lessons whose feature is still in beta; the landing page marks them.
BETA_LESSONS = {"9"}  # MCP connector
BETA_BADGE = " :red[**BETA**]"  # Streamlit markdown: red, bold text (works in buttons and headers)


def lesson_parts(path):
    """(number, letter, name) from the docstring title, e.g. ('5', 'b', 'Structured tool results')."""
    title, _ = description(path)
    match = re.search(r"Lesson (\d+)(\w*) - (.*)", title)
    return (match.group(1), match.group(2), match.group(3)) if match else (path.stem, "", path.stem)


def has_run(path):
    return str(path) in st.session_state.get("results", {})


def variant_label(path):
    """Label of one example inside a lesson, e.g. 'b · Structured tool results'."""
    _, letter, name = lesson_parts(path)
    return ("✓ " if has_run(path) else "") + (f"{letter} · {name}" if letter else name)


def lesson_groups(scripts):
    """{lesson number: [example paths]}, in order, so 5a-5d become one entry '5'."""
    groups_by_number = {}
    for path in scripts:
        groups_by_number.setdefault(lesson_parts(path)[0], []).append(path)
    return groups_by_number


def group_label(number, paths, count=True):
    """Label of a whole lesson, e.g. '5 · Tool use  (4 examples)'. A lesson with one script is just that script."""
    if len(paths) == 1:
        return lesson_label(paths[0])
    name = LESSON_NAMES.get(number, lesson_parts(paths[0])[2])
    suffix = f"  ({len(paths)} examples)" if count else ""
    return ("✓ " if any(has_run(path) for path in paths) else "") + f"{number} · {name}{suffix}"


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
    # None = the landing page. A ?lesson=<name> in the URL (kept on refresh) opens that lesson.
    wanted = st.query_params.get("lesson")
    match = next((p for scripts in groups.values() for p in scripts if p.stem == wanted), None)
    st.session_state.selected = str(match) if match else None
if "results" not in st.session_state:
    st.session_state.results = {}
if "view" not in st.session_state:
    st.session_state.view = "Code"
if "run_requested" not in st.session_state:
    st.session_state.run_requested = False


# While a script runs, keep the newest output in view. Streamlit has no setting for this, so a tiny
# script in an invisible iframe scrolls the page (and the output pane in side-by-side mode) to the
# bottom a few times per second. It stops following as soon as you scroll up, and it disappears
# when the run ends, because the iframe is removed.
AUTOSCROLL_JS = """
<script>
const doc = window.parent.document;
let following = true;
doc.addEventListener("wheel", (event) => { if (event.deltaY < 0) following = false; }, { passive: true });
doc.addEventListener("touchmove", () => { following = false; }, { passive: true });

function scrollTargets() {
  const targets = [doc.querySelector('[data-testid="stMain"]') || doc.querySelector("section.main")];
  for (const element of doc.querySelectorAll("div")) {
    const overflow = getComputedStyle(element).overflowY;
    if ((overflow === "auto" || overflow === "scroll") && element.scrollHeight > element.clientHeight + 5
        && !element.closest('[data-testid="stSidebar"]') && !element.closest('[data-testid="stCode"]')) {
      targets.push(element);
    }
  }
  return targets.filter(Boolean);
}

setInterval(() => {
  if (!following) return;
  for (const element of scrollTargets()) element.scrollTop = element.scrollHeight;
}, 250);
</script>
"""


def toggle_view():
    st.session_state.view = "Code" if st.session_state.view == "Output" else "Output"


def request_run():
    """Run button callback: show the Output view and run on the next rerun."""
    st.session_state.view = "Output"
    st.session_state.run_requested = True

def open_lesson(path):
    st.session_state.selected = str(path)
    st.session_state.view = "Code"


def go_home():
    st.session_state.selected = None


# Keep the lesson in the URL, so a browser refresh does not send you back to the landing page.
if st.session_state.selected:
    st.query_params["lesson"] = Path(st.session_state.selected).stem
elif "lesson" in st.query_params:
    del st.query_params["lesson"]


def render_home():
    """The landing page: what this is, a link to the course, and one card per course section."""
    # A compact banner (80%) next to the course link (20%), both the same height.
    banner, course = st.columns([4, 1])
    banner.markdown(
        """
        <div style="height: 7.5rem; box-sizing: border-box; padding: 0.4rem 1.6rem; border-radius: 14px; color: white;
                    display: flex; flex-direction: column; justify-content: center;
                    background: linear-gradient(135deg, #1f2937 0%, #4b5563 100%);">
          <div style="font-size: 0.85rem; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.85; line-height: 1.2;">
            Practice scripts for the course
          </div>
          <div style="font-size: 2.1rem; font-weight: 700; line-height: 1.1; margin: 0.1rem 0 0.2rem 0;">
            Claude Platform 101
          </div>
          <div style="font-size: 1.05rem; line-height: 1.45; opacity: 0.95;">
            Every lesson as a small, runnable Python script. Read the code, press Run, and watch
            what the API sends and what Claude answers.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    course.markdown(
        f"""
        <a href="{COURSE_URL}" target="_blank" style="text-decoration: none;">
          <div style="height: 7.5rem; box-sizing: border-box; padding: 0.8rem; border-radius: 14px; color: white;
                      display: flex; flex-direction: column; align-items: center; justify-content: center;
                      text-align: center; background: #475569;">
            <img src="data:image/png;base64,{LOGO_BASE64}" alt="Claude" style="height: 2.4rem; width: auto;" />
            <div style="font-weight: 600; margin-top: 0.4rem;">Open the course</div>
            <div style="font-size: 0.85rem; opacity: 0.75;">Anthropic Academy</div>
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    st.subheader("Pick a lesson", anchor=False)
    # Larger text on the cards and their lesson buttons, to make them easier to read.
    st.markdown("<style>[data-testid='stButton'] button p { font-size: 1.1rem; }</style>", unsafe_allow_html=True)
    columns = st.columns(len(groups))
    for column, (folder, scripts) in zip(columns, groups.items()):
        icon, title, text = SECTIONS.get(folder[:2], ("📘", folder, ""))
        with column.container(border=True):
            st.markdown(
                f"<div style='display: flex; align-items: center; justify-content: center; gap: 0.8rem;'>"
                f"<div style='font-size: 2.6rem; line-height: 1;'>{icon}</div>"
                f"<div style='font-weight: 600; font-size: 1.4rem;'>{title}</div></div>",
                unsafe_allow_html=True,
            )
            lessons_here = lesson_groups(scripts)
            count = f"{len(lessons_here)} lesson{'s' if len(lessons_here) != 1 else ''}"
            st.markdown(f"<div style='text-align: center; opacity: 0.6; font-size: 1rem; margin-bottom: 1.4rem;'>{count}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center; font-size: 1.15rem; line-height: 1.5; margin-bottom: 2rem;'>{text}</div>", unsafe_allow_html=True)
            for number, paths in lessons_here.items():
                label = group_label(number, paths) + (BETA_BADGE if number in BETA_LESSONS else "")
                st.button(label, key=f"home-{folder}-{number}",
                          on_click=open_lesson, args=(paths[0],), use_container_width=True)



# ---- Left: the lessons of the current section (hidden on the landing page) -----
if st.session_state.selected is None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    current = Path(st.session_state.selected)
    with st.sidebar:
        st.button("🏠 Home", on_click=go_home, use_container_width=True)
        st.subheader(SECTIONS.get(current.parent.name[:2], ("", current.parent.name, ""))[1], anchor=False)
        for number, paths in lesson_groups(groups[current.parent.name]).items():
            st.button(group_label(number, paths), key=f"nav-{number}", on_click=open_lesson, args=(paths[0],),
                      type="primary" if current in paths else "secondary", use_container_width=True)

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
lesson_number = lesson_parts(script)[0]
examples = lesson_groups(groups[script.parent.name])[lesson_number]
crumb.caption(f"{section_title}  ›  {group_label(lesson_number, examples, count=False)}")
previous_col.button("← Previous", on_click=open_lesson, args=(lessons[max(position - 1, 0)],),
                    disabled=position == 0, use_container_width=True)
next_col.button("Next →", on_click=open_lesson, args=(lessons[min(position + 1, len(lessons) - 1)],),
                disabled=position == len(lessons) - 1, use_container_width=True)

if len(examples) > 1:
    # One lesson, several examples: switch between them here.
    for column, example in zip(st.columns(len(examples)), examples):
        column.button(variant_label(example), key=f"example-{example}", on_click=open_lesson, args=(example,),
                      type="primary" if example == script else "secondary", use_container_width=True)

header = title.removeprefix("Claude Platform 101: ") if title else script.stem
st.header(header + (BETA_BADGE if lesson_number in BETA_LESSONS else ""), anchor=False)
st.write(intro)
if course_url := course_lesson_url(script):
    st.link_button("Open this lesson in the course ↗", course_url)

warning = next((text for prefix, text in WARNINGS.items() if script.name.startswith(prefix)), None)
if warning:
    st.warning(warning)

has_result = str(script) in st.session_state.results
side_by_side = st.session_state.get("side_by_side", False)
showing_output = st.session_state.view == "Output"

siblings = groups[script.parent.name]
previous_in_section = siblings[siblings.index(script) - 1] if siblings.index(script) > 0 else None

col_run, col_clear, col_view, col_side, col_diff, _ = st.columns([1, 1, 2, 2, 2.6, 1.4])
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
col_diff.toggle(
    "Diff vs previous", key="show_diff",
    disabled=previous_in_section is None or (showing_output and not side_by_side),
)


def render_code(height="content"):
    """The lesson's code, or what changed since the previous lesson of the section."""
    if st.session_state.get("show_diff") and previous_in_section:
        diff = "".join(difflib.unified_diff(
            previous_in_section.read_text(encoding="utf-8").splitlines(keepends=True),
            script.read_text(encoding="utf-8").splitlines(keepends=True),
            fromfile=previous_in_section.name, tofile=script.name, n=3,
        ))
        st.caption(f"Changes from {lesson_label(previous_in_section)}")
        st.code(diff or "(no differences)", language="diff", height=height)
    else:
        st.code(script.read_text(encoding="utf-8"), language="python", line_numbers=True, height=height)


def render_output(container):
    """Run the script if Run was pressed, then show its saved result in the container."""
    with container:
        box = st.empty()
        if st.session_state.run_requested:
            st.session_state.run_requested = False
            scroller = st.empty()
            with scroller:
                components.html(AUTOSCROLL_JS, height=0)
            try:
                with st.spinner("Running..."):
                    output, code, seconds = run(script, box)
            finally:
                scroller.empty()   # removes the iframe, which stops the scrolling
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
        render_code(height=700)
    render_output(right.container(height=700))
elif showing_output:
    render_output(st.container())
else:
    render_code()
