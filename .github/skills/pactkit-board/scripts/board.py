import abc, re, os, sys, json, datetime, argparse, subprocess, shutil, ast
from collections import deque
from dataclasses import dataclass
from pathlib import Path

def nl(): return chr(10)

# Shared pattern for all recognized work item prefixes
ITEM_ID_RE = r"(?:STORY|HOTFIX|BUG)(?:-[a-z]+)?-\d+"

# Flexible story title pattern: matches ### or #### (tolerant) with [ID] or ID: or ID formats
# Group 1: story ID, Group 2: title text
# BUG-027: Support both ### and #### for backward compatibility
_TITLE_RE = rf"^#{{3,4}} \[?({ITEM_ID_RE})\]?:?\s*(.*)"

# Section markers
# STORY-slim-007: canonical values defined in src/pactkit/schemas.py BOARD_SECTION_*.
# This standalone script cannot import pactkit, so values are inlined here.
# When updating, also update src/pactkit/schemas.py.
_BACKLOG = "## 📋 Backlog"
_IN_PROGRESS = "## 🔄 In Progress"
_DONE = "## ✅ Done"


def _story_repository():
    """Load the Core-owned repository or fail without touching legacy views."""
    try:
        from pactkit.governance import StoryRepository
    except ImportError as exc:
        raise RuntimeError(
            "pactkit Core with sharded governance support is required; run `pip install -U pactkit`"
        ) from exc
    return StoryRepository(Path.cwd())


# --- BOARD ---
def add_story(sid, title, tasks):
    try:
        _story_repository().add(sid, title, [task.strip() for task in tasks.split("|") if task.strip()])
        return f"✅ Story {sid} added"
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"


def _parse_story_blocks(content):
    """Extract all ### [ID] or ### ID: blocks with their full text and positions.

    Returns list of (sid, block_text, start_pos, end_pos) tuples.
    """
    blocks = []
    story_pat = _TITLE_RE
    section_pat = r"^## "
    matches = list(re.finditer(story_pat, content, re.MULTILINE))
    # Find all section header positions to use as boundaries
    section_starts = [m.start() for m in re.finditer(section_pat, content, re.MULTILINE)]
    for i, m in enumerate(matches):
        start = m.start()
        # End at the next story header, next section header, or EOF
        next_story = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        next_section = len(content)
        for sp in section_starts:
            if sp > start:
                next_section = sp
                break
        end = min(next_story, next_section)
        # R4 (STORY-slim-052): Trim trailing whitespace and adjust end to match,
        # so that len(block_text) == end - start for all callers.
        raw = content[start:end]
        trimmed = raw.rstrip()
        adjusted_end = start + len(trimmed)
        blocks.append((m.group(1), trimmed, start, adjusted_end))
    return blocks


def fix_board():
    """Regenerate the deterministic projection; never infer facts from it."""
    try:
        from pactkit.governance import BoardRenderer
        from pactkit.utils import atomic_write

        repository = _story_repository()
        path = Path.cwd() / "docs/product/sprint_board.md"
        atomic_write(path, BoardRenderer(repository).render())
        return f"✅ Board projection rendered: {len(repository.list())} stories."
    except (RuntimeError, ValueError, OSError) as exc:
        return f"❌ {exc}"


def add_task(sid, task_title):
    try:
        _story_repository().add_task(sid, " ".join(task_title))
        return f"✅ Task added to {sid}"
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"


def update_task(sid, tasks_list):
    task_name = " ".join(tasks_list)
    try:
        _story_repository().complete_task(sid, task_name)
        return f"✅ Task {sid} updated: {task_name}"
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"



def snapshot_graph(version):
    graphs_dir = Path.cwd() / "docs/architecture/graphs"
    snap_dir = Path.cwd() / "docs/architecture/snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for name in ["code_graph.mmd", "class_graph.mmd", "call_graph.mmd"]:
        src = graphs_dir / name
        if src.exists():
            shutil.copy2(src, snap_dir / f"{version}_{name}")
            count += 1
    return f"✅ Snapshot {version}: {count} graphs saved"


# --- MOVE ---
def move_story(sid, target):
    """Move a story to the specified section regardless of checkbox state."""
    try:
        _story_repository().move(sid, target)
        return f"✅ Moved {sid} to {target}"
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"


# --- LIST ---
def list_stories():
    try:
        records = _story_repository().list()
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"
    if not records:
        return "No stories on board."
    return nl().join(
        f"{record['id']} | {record['title']} | "
        f"{sum(task['completed'] for task in record['tasks'])}/{len(record['tasks'])} | "
        f"{record['status'].upper()}"
        for record in records
    )


# --- ARCHIVE ---
def archive_stories():
    try:
        repository = _story_repository()
        completed = [record for record in repository.list() if record["status"] == "done"]
        for record in completed:
            repository.move(record["id"], "archived")
        if not completed:
            return "✅ No completed stories to archive."
        return f"✅ Archived {len(completed)} Story records"
    except (RuntimeError, ValueError) as exc:
        return f"❌ {exc}"


# --- CLI ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add_story")
    p_add.add_argument("story_id")
    p_add.add_argument("title")
    p_add.add_argument("tasks")
    p_addtask = sub.add_parser("add_task")
    p_addtask.add_argument("story_id")
    p_addtask.add_argument("task_title", nargs="+")
    p_upd = sub.add_parser("update_task")
    p_upd.add_argument("story_id")
    p_upd.add_argument("task_name", nargs="+")
    p_snap = sub.add_parser("snapshot")
    p_snap.add_argument("version")
    p_move = sub.add_parser("move_story")
    p_move.add_argument("story_id")
    p_move.add_argument("target", choices=["backlog", "in_progress", "done"])
    sub.add_parser("archive")
    sub.add_parser("list_stories")
    sub.add_parser("fix_board")
    p_render = sub.add_parser("render")
    p_render.add_argument("--check", action="store_true")

    a = parser.parse_args()
    if a.cmd == "add_story":
        print(add_story(a.story_id, a.title, a.tasks))
    elif a.cmd == "add_task":
        print(add_task(a.story_id, a.task_title))
    elif a.cmd == "update_task":
        print(update_task(a.story_id, a.task_name))
    elif a.cmd == "snapshot":
        print(snapshot_graph(a.version))
    elif a.cmd == "archive":
        print(archive_stories())
    elif a.cmd == "list_stories":
        print(list_stories())
    elif a.cmd == "move_story":
        print(move_story(a.story_id, a.target))
    elif a.cmd == "fix_board":
        print(fix_board())
    elif a.cmd == "render":
        from pactkit.governance import BoardRenderer
        from pactkit.utils import atomic_write

        repository = _story_repository()
        output = Path.cwd() / "docs/product/sprint_board.md"
        renderer = BoardRenderer(repository)
        if a.check:
            if not renderer.check(output):
                print("❌ Board projection drift")
                raise SystemExit(1)
            print("✅ Board projection current")
        else:
            atomic_write(output, renderer.render())
            print(f"✅ Board projection rendered: {output}")
