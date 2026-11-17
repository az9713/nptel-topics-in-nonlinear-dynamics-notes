from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "plan/chapters.json").read_text(encoding="utf-8-sig"))
ESC = html.escape


def read_lectures():
    with (ROOT / "lecture-inventory.csv").open(encoding="utf-8-sig", newline="") as file:
        return {int(row["lecture"]): row for row in csv.DictReader(file)}


def render_markdown(text):
    fragments = []
    pattern = re.compile(
        r"(?ms)^\x60{3,}.*?^\x60{3,}[^\S\n]*$|\x60[^\x60\n]+\x60|"
        r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<![\\$])\$([^$\n]+?)(?<!\\)\$(?!\$)"
    )

    def protect(match):
        expression = match.group()
        if expression.startswith(chr(96)):
            return expression
        is_display = expression.startswith("$$")
        tex = expression[2:-2].strip() if is_display else expression[1:-1]
        left, right = (r"\[", r"\]") if is_display else (r"\(", r"\)")
        if is_display:
            fragment = f'<div class="equation">{left}{ESC(tex)}{right}</div>'
            token = f"\n\n<div data-equation=\"{len(fragments)}\"></div>\n\n"
        else:
            fragment = f'<span class="math">{left}{ESC(tex)}{right}</span>'
            token = f'<span data-equation="{len(fragments)}"></span>'
        fragments.append(fragment)
        return token

    protected = pattern.sub(protect, text)
    rendered = markdown.markdown(
        protected,
        extensions=["extra", "toc"],
        extension_configs={"toc": {"toc_depth": "2"}}
    )

    def restore(match):
        return fragments[int(match.group(1))]

    rendered = rendered.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>"
    )
    return re.sub(r'<(?:span|div) data-equation="(\d+)"></(?:span|div)>', restore, rendered)


def page(title, body, *, prefix="", class_name="reading", math=False, search=False):
    if math:
        scripts = (
            f'<script defer src="{prefix}assets/math-config.js"></script>'
            f'<script defer src="{prefix}assets/mathjax-tex-svg.js"></script>'
            f'<script defer src="{prefix}assets/reader.js"></script>'
        )
    else:
        scripts = ""
    if search:
        scripts += f'<script defer src="{prefix}assets/search.js"></script>'
    nav = "".join(
        f'<a href="{prefix}{url}">{label}</a>'
        for url, label in [
            ("index.html", "Chapters"), ("study-guide.html", "Study guide"),
            ("source-map.html", "Lectures"), ("laboratory.html", "Labs"),
        ]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<title>{ESC(title)} · Topics in Nonlinear Dynamics</title>
<link rel="stylesheet" href="{prefix}assets/reader.css">
{scripts}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="{prefix}index.html">Topics in Nonlinear Dynamics</a>
  <nav aria-label="Reader">{nav}</nav>
</header>
<main id="main" class="{class_name}">{body}</main>
<footer>Independent study edition · <a href="{ESC(PLAN["course"])}">NPTEL course</a></footer>
</body>
</html>
"""


def write(relative, text):
    (ROOT / relative).write_text(text, encoding="utf-8", newline="\n")


def chapter_link(chapter, label, prefix=""):
    return f'<a href="{prefix}chapters/ch{chapter:02}.html">{ESC(label)}</a>'


def lecture_link(lecture, item, *, title=False):
    label = f'{lecture}. {item["title"]}' if title else f"L{lecture}"
    return f'<a href="https://www.youtube.com/watch?v={item["video_id"]}">{ESC(label)}</a>'


def build(*, preview=False):
    lectures = read_lectures()
    chapter_plan = PLAN["chapters"]
    ready = {
        number for number in range(1, len(chapter_plan) + 1)
        if all((ROOT / path).exists() for path in [
            f"chapters/ch{number:02}.md", f"code/ch{number:02}.py"
        ])
    }
    if not preview and len(ready) != len(chapter_plan):
        missing = sorted(set(range(1, len(chapter_plan) + 1)) - ready)
        raise ValueError(f"Missing chapter/lab pairs: {missing}")

    cards, source_rows, labs = [], [], []
    artifacts = []
    for number, (first, last, _) in enumerate(chapter_plan, 1):
        if number not in ready:
            continue
        draft = (ROOT / f"chapters/ch{number:02}.md").read_text(encoding="utf-8-sig")
        title_line, _, manuscript = draft.partition("\n")
        if not title_line.startswith("# "):
            raise ValueError(f"Chapter {number} must start with a level-one title")
        chapter_title = title_line[2:].strip()
        sources = " ".join(lecture_link(i, lectures[i]) for i in range(first, last + 1))
        previous = (
            chapter_link(number - 1, "← Previous chapter", "../")
            if number - 1 in ready else ""
        )
        following = (
            chapter_link(number + 1, "Next chapter →", "../")
            if number + 1 in ready else ""
        )
        end_nav = f'<nav class="chapter-nav" aria-label="Chapter order">{previous}{following}</nav>'
        opening, separator, sections = manuscript.partition("\n## ")
        with_toc = opening + "\n\n[TOC]\n\n" + separator + sections
        content = render_markdown(with_toc)
        heading = (
            f'<p class="context">Chapter {number} · <a href="../source-map.html#l{first:02}">'
            f'Lectures {first}–{last}</a></p><h1>{ESC(chapter_title)}</h1>'
            f'<nav class="recordings" aria-label="Source recordings">{sources}</nav>'
        )
        write(f"chapters/ch{number:02}.html",
              page(chapter_title, heading + content + end_nav, prefix="../", math=True))
        dependencies = [f"L{i:02}" for i in range(first, last + 1)]
        artifacts.extend([
            {"path": f"chapters/ch{number:02}.html", "purpose": "Reading edition",
             "source_dependencies": dependencies},
            {"path": f"chapters/ch{number:02}.md", "purpose": "Editable manuscript",
             "source_dependencies": dependencies},
            {"path": f"code/ch{number:02}.py", "purpose": "Reproducible model check",
             "source_dependencies": dependencies},
        ])
        topics = " · ".join(ESC(lectures[i]["title"]) for i in range(first, last + 1))
        cards.append(
            f'<li value="{number}"><h3>{chapter_link(number, chapter_title)}</h3>'
            f'<p class="context">Lectures {first}–{last}</p><p>{topics}</p></li>'
        )
        labs.append(
            f'<li>{chapter_link(number, chapter_title)}'
            f'<a href="code/ch{number:02}.py" download>Python source</a></li>'
        )
        for i in range(first, last + 1):
            item = lectures[i]
            source_rows.append(
                f'<tr id="l{i:02}"><td>{lecture_link(i, item, title=True)}</td>'
                f'<td>{chapter_link(number, f"Chapter {number}")}</td>'
                f'<td>{ESC(item["source_basis"])}</td></tr>'
            )

    groups = [("Flows and Hamiltonian mechanics", 0, 4),
              ("Bifurcations, oscillations, and discrete maps", 4, 9),
              ("Coarse graining and stochastic dynamics", 9, len(chapter_plan))]
    if preview:
        contents = '<ol class="chapters">' + "".join(cards) + '</ol>'
    else:
        contents = "".join(
            f'<section><h2>{title}</h2><ol class="chapters" start="{start + 1}">'
            + "".join(cards[start:stop]) + "</ol></section>"
            for title, start, stop in groups
        )
    index = (
        '<div class="intro"><p class="context">Independent notes for NPTEL course 115106059</p>'
        '<h1>Topics in Nonlinear Dynamics</h1><p class="summary">Use vector fields, '
        'invariants, and probability to explain what happens to trajectories as '
        'initial conditions, parameters, and the scale of observation change.</p>'
        f'<p class="context">V. Balakrishnan · IIT Madras · {len(lectures)} recordings · '
        f'{len(ready)} chapters</p></div>'
        '<div class="search" role="search" hidden><label for="chapter-query">Filter by topic</label>'
        '<input id="chapter-query" type="search" autocomplete="off">'
        '<p id="chapter-count" aria-live="polite"></p></div>' + contents
    )
    write("index.html", page("Course reader", index, class_name="catalog", search=True))
    source_intro = (
        '<h1>Lecture map</h1><p>Each recording is linked in playlist order. '
        'The notes include independent examples, proofs, and computational experiments. '
        'Section links use caption cues when confirmed. '
        'Automatic English captions provide evidence for topic order and timing. '
        'They can misrecognize mathematical notation. The project used caption text '
        'and linked course materials. Audio and board images were outside the systematic review.</p>'
        f'<p><a href="{ESC(PLAN["playlist"])}">Watch the NPTEL playlist</a> · '
        '<a href="lecture-inventory.csv">Download the lecture inventory</a></p>'
    )
    if preview:
        assigned = {i for number, (first, last, _) in enumerate(chapter_plan, 1)
                    if number in ready for i in range(first, last + 1)}
        for i, item in lectures.items():
            if i not in assigned:
                source_rows.append(f'<tr id="l{i:02}"><td>{lecture_link(i, item, title=True)}</td>'
                                   f'<td>In preparation</td><td>{ESC(item["source_basis"])}</td></tr>')
        source_rows.sort()
    write("source-map.html", page("Lecture map", source_intro +
          '<div class="table-wrap"><table><thead><tr><th>Recording</th><th>Notes</th>'
          '<th>Source</th></tr></thead><tbody>' + "".join(source_rows) +
          '</tbody></table></div>', class_name="catalog"))
    write("laboratory.html", page("Laboratories", '<h1>Laboratories</h1><p>Install '
          '<code>requirements.txt</code>. Run a lab with <code>python code/ch01.py</code> '
          'or change the chapter number. Each script checks its results with assertions.'
          '</p><ol class="lab-list">' + "".join(labs) + '</ol>'))
    guide = (ROOT / "plan/study-guide.md").read_text(encoding="utf-8-sig")
    write("study-guide.html", page("Study guide", render_markdown(guide), math=True))
    sources = []
    for i, item in lectures.items():
        sources.append({
            "id": f"L{i:02}",
            "input": f'https://www.youtube.com/watch?v={item["video_id"]}',
            "title": item["title"],
            "duration_seconds": int(item["duration_seconds"]),
            "status": "caption acquired" if item["caption_sha256"] else "metadata only",
            "coverage": {
                "representation": item["source_basis"],
                "track": item["caption_track"],
                "sha256": item["caption_sha256"],
                "first_cue_seconds": int(item["caption_start"]) if item["caption_start"] else None,
                "last_cue_end_seconds": int(item["caption_end"]) if item["caption_end"] else None,
            },
        })
    convenience = {
        "index.html": "Course catalog and chapter search",
        "study-guide.html": "Learning sequence and official course resources",
        "source-map.html": "Recordings in playlist order",
        "lecture-inventory.csv": "Caption and playlist provenance in tabular form",
        "laboratory.html": "Index of computational laboratories",
    }
    artifacts.extend({"path": path, "purpose": purpose,
                      "source_dependencies": [source["id"] for source in sources]}
                     for path, purpose in convenience.items())
    for path, data in [
        ("source-manifest.json", {"playlist": PLAN["playlist"], "course": PLAN["course"],
                                  "sources": sources}),
        ("artifact-manifest.json", {"preview": preview, "artifacts": artifacts}),
    ]:
        write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build the nonlinear dynamics reader.")
    parser.add_argument("--preview", action="store_true", help="Render available chapters.")
    build(preview=parser.parse_args().preview)
