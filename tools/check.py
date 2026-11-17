"""Check the lecture inventory, generated site, and chapter laboratories."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import parse_qs, unquote, urlsplit

from build import PLAN, ROOT, build, read_lectures


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, ("duplicate id", attrs["id"])
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    lectures = read_lectures()
    ids = {row["video_id"]: (number, int(row["duration_seconds"]))
           for number, row in lectures.items()}
    assert len(lectures) == len(ids) == 29
    assert all(re.fullmatch(r"[\w-]{11}", video_id) for video_id in ids)
    assert all(re.fullmatch(r"[a-f0-9]{64}", row["caption_sha256"])
               and 0 <= int(row["caption_start"]) < int(row["caption_end"])
               and int(row["caption_end"]) - int(row["duration_seconds"]) <= 5
               for row in lectures.values())
    assigned = [number for first, last, _ in PLAN["chapters"]
                for number in range(first, last + 1)]
    assert assigned == list(lectures)
    build(preview=args.preview)
    page_paths = [ROOT / name for name in ("index.html", "study-guide.html",
                                           "source-map.html", "laboratory.html")]
    notes = []
    for number, (first, last, _) in enumerate(PLAN["chapters"], 1):
        source = ROOT / f"chapters/ch{number:02}.md"
        lab = ROOT / f"code/ch{number:02}.py"
        if args.preview and not (source.is_file() and lab.is_file()):
            continue
        material = source.read_text(encoding="utf-8-sig")
        assert "<details" in material and "## " in material, source
        assert not re.search(r"\[(?:PROOF|CITATION|AUTHOR DECISION|NUMBER) (?:NEEDED|NOT YET)", material)
        chapter_lectures = set()
        timestamp_count = 0
        for target in re.findall(r"https://www\.youtube\.com/watch\?[^)\s<>]+", material):
            query = parse_qs(urlsplit(target.replace("&amp;", "&")).query)
            if "t" not in query:
                continue
            position, duration = ids[query["v"][0]]
            seconds = int(query["t"][0].removesuffix("s"))
            assert 0 <= seconds < duration, (source, target)
            assert first <= position <= last, (source, target)
            chapter_lectures.add(position)
            timestamp_count += 1
        assert chapter_lectures == set(range(first, last + 1)), (source, chapter_lectures)
        command = [sys.executable, "-X", "utf8", str(lab)]
        output = subprocess.check_output(command, cwd=ROOT, encoding="utf-8", timeout=90)
        repeated = subprocess.check_output(command, cwd=ROOT, encoding="utf-8", timeout=90)
        assert repeated == output, (lab, "nondeterministic output")
        notes.append(dict(chapter=number, manuscript_sha256=sha256(source),
                          lecture_timestamps=timestamp_count,
                          lab_sha256=sha256(lab), lab_stdout=output))
        page_paths.append(source.with_suffix(".html"))

    pages = {path: Page(path.read_text(encoding="utf-8")) for path in page_paths}
    for path, page in pages.items():
        for link in page.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            destination = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            if (args.preview and destination.parent == ROOT / "chapters"
                    and re.fullmatch(r"ch\d{2}\.html", destination.name)
                    and destination not in pages):
                continue
            assert destination.is_relative_to(ROOT) and destination.is_file(), (path, link)
            if parts.fragment and destination in pages:
                assert unquote(parts.fragment) in pages[destination].ids, (path, link)
    before = {path: sha256(path) for path in pages}
    build(preview=args.preview)
    assert all(sha256(path) == digest for path, digest in before.items())
    report = {"preview": args.preview, "lectures_in_inventory": len(lectures),
              "pages_checked": len(pages), "chapters": notes,
              "static_reader_rebuild_identical": True}
    destination = ROOT / ("work" if args.preview else "validation") / "checks.json"
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(f"Validated {len(lectures)} inventory records, {len(notes)} chapter labs, "
          f"and {len(pages)} reader pages")


if __name__ == "__main__":
    main()
