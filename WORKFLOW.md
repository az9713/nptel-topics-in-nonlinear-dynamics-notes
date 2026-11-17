# Lecture-note production workflow

The plan follows the local NPTEL Matrix Theory reader and the transcript-grounded workflow of the Stanford CS229 and NPTEL Mathematical Foundations for Machine Learning editions.

1. Inventory the exact supplied YouTube playlist in upload order and verify the instructor and course identity against NPTEL. Preserve the 29 entries, including both quizzes.
2. Acquire the best available English captions. Preserve hashes and observed timing in [the lecture inventory](lecture-inventory.csv). Keep the JSON3 files and normalized cues under ignored work/. The English original tracks are automatic. Caption endpoints measure timing coverage.
3. Group consecutive lectures by the argument they develop. Read cue text in sequence and record exact section anchors and source limits. Chapter manuscripts and exercises are original exposition. Flag original constructions, additional proofs, and research extensions near the claims.
4. Use transcript-grounded-textbook, rigorous-explainer, and science-editor, with supporting source analysis. Match the complete exemplars in definitions, derivations, original cases, solved exercises, lab checks, and attribution. Chapters develop one mathematical case across sections where the topic permits it.
5. Run independent mathematical and editorial reviews and record fixes. Exact manuscript hashes identify what was reviewed. An assertion in a numerical lab supports that computation. Scientific review judges the hypotheses and conclusions stated in the chapter.
6. Build the static reader with local MathJax. Check local links, coverage, timestamp bounds, exact chapter pairs, lab outputs and repeatability, and offline rendering at desktop and phone widths. Keep public-ready reader inputs independent of the caption directory.
7. Audit the staged release. GitHub Actions checks the exact archived site at desktop and phone widths before deploying it to GitHub Pages. Verify the live files and browser behavior after deployment.

## Local commands

From the project root, install requirements with python -m pip install -r requirements.txt. Generate the reader with python tools/build.py. Pass --preview to render the chapters with available manuscript and code pairs during authoring.

Run python tools/check.py for source, link, and lab checks. Run python tools/browser_check.py for browser checks and python tools/check_math_layout.py followed by the chapter paths for equation layout. Both use Playwright and support a local Chromium installation.

Regenerate the three original diagrams with python tools/phase_portrait.py and python tools/course_figures.py.

The source ledgers are local working documents. The coverage pass used caption cues in recording order and targeted passages to verify specific boundaries. It did not independently verify every spoken word, every board diagram, or every equation written during the recordings.

## GitHub Pages

The [publication workflow](.github/workflows/publish.yml) runs for pull requests to main, pushes to main, and manual dispatches. The check runs the MathJax layout validator on every chapter at widths of 1440 and 390 pixels. A successful main-branch run deploys the checked archive. README.txt, caption downloads, and local working files are excluded from the release.
