from __future__ import annotations

import argparse
import json
import re

from playwright.sync_api import sync_playwright

from build import PLAN, ROOT


def main():
    parser = argparse.ArgumentParser(description="Check rendered reader pages.")
    parser.add_argument("--browser", help="Path to a Chromium browser executable")
    parser.add_argument("--base-url", help="HTTP(S) reader directory, or use local files")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    pages = ["index.html", "source-map.html", "study-guide.html", "laboratory.html"]
    pages.extend(
        f"chapters/ch{number:02}.html"
        for number in range(1, len(PLAN["chapters"]) + 1)
        if not args.preview or (ROOT / f"chapters/ch{number:02}.html").is_file()
    )
    failures, results = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser)
        for width, height in [(1440, 900), (390, 844)]:
            tab = browser.new_page(viewport={"width": width, "height": height})
            tab.on("pageerror", lambda error: failures.append(str(error)))
            if not args.base_url:
                def reject_network(route):
                    failures.append(f"External request in offline reader: {route.request.url}")
                    route.abort()
                tab.route(re.compile(r"^https?:"), reject_network)
            for path in pages:
                url = (f"{args.base_url.rstrip('/')}/{path}" if args.base_url
                       else (ROOT / path).as_uri())
                reply = tab.goto(url, wait_until="load")
                if args.base_url:
                    assert reply and reply.ok, url
                assert tab.locator("h1").count() == 1, path
                has_math = tab.locator("script[src$='mathjax-tex-svg.js']").count()
                if has_math:
                    tab.evaluate("() => MathJax.startup.promise.then(() => undefined)")
                rendered = tab.locator("mjx-container").count()
                errors = tab.locator("mjx-merror").all_text_contents()
                pending = tab.locator(".math, .equation").evaluate_all(
                    "(nodes) => nodes.filter(n => !n.querySelector('mjx-container')).length"
                )
                broken_images = tab.locator("img").evaluate_all(
                    "(nodes) => nodes.filter(n => !n.complete || !n.naturalWidth).length"
                )
                if path == "index.html" and not args.preview:
                    chapter_input = tab.locator("#chapter-query")
                    chapter_input.fill("linearization")
                    assert tab.locator(".chapters li:visible").count() == 1
                    chapter_input.fill("no such dynamics topic xyzxyz")
                    assert tab.locator(".chapters li:visible").count() == 0
                    chapter_input.fill("")
                    assert tab.locator(".chapters li:visible").count() == len(PLAN["chapters"])
                if path.startswith("chapters/"):
                    for solution in tab.locator("details").all():
                        summary = solution.locator("summary")
                        initial = solution.evaluate("node => node.open")
                        summary.click()
                        assert solution.evaluate("node => node.open") != initial, path
                        summary.click()
                        tab.evaluate("window.dispatchEvent(new Event('beforeprint'))")
                        assert solution.evaluate("node => node.open"), path
                        tab.evaluate("window.dispatchEvent(new Event('afterprint'))")
                        assert solution.evaluate("node => node.open") == initial, path
                overflow = tab.evaluate(
                    "() => document.documentElement.scrollWidth > window.innerWidth"
                )
                if (has_math and "/ch" in path and not rendered) or errors or pending or overflow or broken_images:
                    failures.append(f"{path} @ {width}: math={rendered} errors={errors}, "
                                    f"unrendered={pending} overflow={overflow} broken_images={broken_images}")
                results.append({"page": path, "width": width, "math_elements": rendered})
            tab.close()
        browser.close()
    if failures:
        raise ValueError("\n".join(failures))
    report_name = "live-browser.json" if args.base_url else "browser.json"
    location = ROOT / ("work" if args.preview else "validation") / report_name
    location.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Passed {len(results)} rendered desktop/mobile checks")


if __name__ == "__main__":
    main()
