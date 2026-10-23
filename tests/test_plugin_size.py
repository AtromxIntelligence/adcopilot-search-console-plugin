"""The plugin directory's size limits, held here so no file grows past them
unnoticed.

The directory's pre-submission checklist says "Keep every file that isn't an
image or font under 256 KiB", and a version that has one is "Held for a
reviewer"; it also says "Keep the plugin to 512 files or fewer". At 0.2.14 of AdCopilot's main plugin the
structural tests were one file, `tests/test_structure.py`, of 273,469 bytes:
11,325 bytes over, and nothing in this repository measured it. 0.2.15 split it
by topic and added this test.

It measures every file in the plugin folder (tracked ones, plus untracked ones
that are not ignored, so a new file fails here before it is committed) and
fails on any file that is not an image or a font and is over 250 KiB, or on a
plugin of more than 480 files. Both limits sit a little under the directory's,
so the check fires while there is still room to act. The message names the
file.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; CI runs it in checks.yml).
"""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KIB = 1024
# The directory's limits are 256 KiB and 512 files.
LIMIT_BYTES = 250 * KIB
LIMIT_FILES = 480
# The files the size limit leaves out. SVG is not among them: it is text, so a
# large one is counted like any other file.
IMAGE_OR_FONT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".bmp",
    ".tif", ".tiff", ".heic",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
}
# Never part of the plugin, and never in what the directory reads.
SKIP_DIRS = {".git", "__pycache__"}


def plugin_files(root=ROOT):
    """(relative name, size in bytes) for every file in the plugin folder."""
    names = None
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root,
                             capture_output=True, text=True, check=True).stdout.strip()
        if Path(top).resolve() == Path(root).resolve():
            out = subprocess.run(
                ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                cwd=root, capture_output=True, check=True).stdout
            names = [n for n in out.decode("utf-8").split("\0") if n]
    except (OSError, subprocess.CalledProcessError):
        names = None
    if names is None:
        # Not a checkout of its own (a copied or unpacked plugin): walk it.
        names = []
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                if not f.endswith(".pyc"):
                    names.append(os.path.relpath(os.path.join(dirpath, f), root))
    found = []
    for name in sorted(set(names)):
        path = Path(root) / name
        if path.is_file():  # a tracked file deleted but not yet staged is not one
            found.append((name, path.stat().st_size))
    return found


def violations(files, limit_bytes=LIMIT_BYTES, limit_files=LIMIT_FILES):
    """The failures among `files`, a list of (name, size), one message each.
    A file over the size limit is named; so are the folders that hold the most
    files when there are too many."""
    messages = []
    for name, size in files:
        if os.path.splitext(name)[1].lower() in IMAGE_OR_FONT:
            continue
        if size > limit_bytes:
            messages.append(
                "%s is %s bytes (%.1f KiB), over %d KiB. The directory holds a "
                "version with a file over 256 KiB, other than an image or a "
                "font, for a reviewer: split the file by topic." %
                (name, format(size, ","), size / KIB, limit_bytes // KIB))
    if len(files) > limit_files:
        per_folder = {}
        for name, _size in files:
            folder = os.path.dirname(name) or "."
            per_folder[folder] = per_folder.get(folder, 0) + 1
        biggest = sorted(per_folder.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        messages.append(
            "the plugin has %d files, over %d (the directory's limit is 512); "
            "most are in %s." %
            (len(files), limit_files,
             ", ".join("%s (%d)" % kv for kv in biggest)))
    return messages


class PluginSize(unittest.TestCase):

    def test_no_file_is_over_the_directorys_size_limit_and_the_plugin_is_small_enough(self):
        files = plugin_files()
        # The scan reads the plugin: it has skills, commands and tests.
        self.assertGreater(len(files), 10)
        self.assertIn(("LICENSE", (ROOT / "LICENSE").stat().st_size), files)
        problems = violations(files)
        self.assertEqual(problems, [], "over the plugin directory's limits:\n"
                         + "\n".join(problems))

    def test_the_check_names_the_file_and_leaves_images_and_fonts_alone(self):
        limit = LIMIT_BYTES
        files = [
            ("tests/too_big.py", limit + 1),      # one byte over: named
            ("README.md", limit),                 # exactly at the limit: fine
            ("skills/a/SKILL.md", 10),
            ("images/sample.png", limit * 10),        # an image: left alone
            ("fonts/Inter.woff2", limit * 10),        # a font: left alone
            ("docs/diagram.SVG", limit + 5),          # text, so counted
        ]
        problems = violations(files)
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(problems[0].startswith("tests/too_big.py is "), problems)
        self.assertTrue(problems[1].startswith("docs/diagram.SVG is "), problems)
        # A file at the limit, a small one, an image and a font: nothing to say.
        self.assertEqual(violations(files[1:5]), [])
        self.assertEqual(violations([("a.md", 1)] * 3, limit_files=3), [])
        many = [("skills/s%d.md" % i, 1) for i in range(4)]
        count = violations(many, limit_files=3)
        self.assertEqual(len(count), 1, count)
        self.assertIn("the plugin has 4 files, over 3", count[0])
        self.assertIn("skills (4)", count[0])


if __name__ == "__main__":
    unittest.main()
