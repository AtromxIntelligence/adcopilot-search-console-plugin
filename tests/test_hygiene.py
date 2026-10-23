"""What the plugin directory's scanner holds, or blocks, anywhere in a plugin:
a credential read from the person's environment, a package launcher, a
download-and-execute pattern, system files, links, a bundled server, a price,
and a name that reads as another company's.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; CI runs it in checks.yml). Nothing here reads the environment.

Every pattern below is built by joining short strings, so that this file never
matches itself. The scan covers every file in the plugin folder that is not an
image, this file and the tests included: the directory reads the tests too.
"""

import os
import re
import unittest
from pathlib import Path

from test_plugin_size import IMAGE_OR_FONT, plugin_files

ROOT = Path(__file__).resolve().parents[1]

# Reading a credential: the environment, or a header that carries one.
CREDENTIAL_PATTERNS = [
    re.escape("os." + "environ"),
    re.escape("getenv" + "("),
    re.escape("process" + ".env"),
    r"\$\{[A-Za-z_]*(?:TOKEN|SECRET|KEY|PASSWORD)[A-Za-z_]*\}",
    re.escape("Authorization" + ":"),
    re.escape("Bearer" + " "),
]
# A command that downloads a package and runs it.
LAUNCHER_PATTERNS = [
    r"\b" + "np" + "x" + r"\b",
    r"\b" + "bun" + "x" + r"\b",
    "pnpm" + r"\s+" + "dlx",
    "yarn" + r"\s+" + "dlx",
    r"\b" + "uv" + "x" + r"\b",
    "pipx" + r"\s+" + "run",
    r"\b" + "uv" + r"\s+" + "run" + r"\b",
]
# A fetch piped into a shell. The one workflow that greps for it names it, so
# that file is left out of this check, as it is left out of its own grep.
DOWNLOAD_AND_EXECUTE = (r"(?:cur" + "l|wge" + "t)[^|;\n]*\\|[ \t]*(?:sudo[ \t]+)?(?:ba)?" + "sh")
EXEMPT_FROM_DOWNLOAD_CHECK = {".github/workflows/checks.yml"}
FORBIDDEN_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "__MACOSX",
                   ".gitmodules", ".gitattributes", "CLAUDE.md"}
FORBIDDEN_SUFFIXES = (".mcpb", ".dxt")
FORBIDDEN_FOLDERS = ("bin",)
OWNERS = ["Google", "Meta", "LinkedIn", "X", "TikTok", "Microsoft"]
# The one sentence that may speak about plans.
PRICING_SENTENCE = ("Free plan available; paid plans on https://adcopilot.cloud/pricing")


def text_files():
    out = []
    for name, _size in plugin_files(ROOT):
        if os.path.splitext(name)[1].lower() in IMAGE_OR_FONT:
            continue
        out.append(name)
    return out


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class Hygiene(unittest.TestCase):

    def test_there_are_files_to_scan(self):
        self.assertGreater(len(text_files()), 10)

    def test_no_file_reads_a_credential(self):
        for name in text_files():
            text = read(name)
            for pattern in CREDENTIAL_PATTERNS:
                self.assertIsNone(re.search(pattern, text), "%s matches %s" % (name, pattern))

    def test_no_file_runs_a_package_launcher(self):
        for name in text_files():
            text = read(name)
            for pattern in LAUNCHER_PATTERNS:
                self.assertIsNone(re.search(pattern, text), "%s matches %s" % (name, pattern))

    def test_no_file_holds_a_download_and_execute_pattern(self):
        for name in text_files():
            if name in EXEMPT_FROM_DOWNLOAD_CHECK:
                continue
            self.assertIsNone(re.search(DOWNLOAD_AND_EXECUTE, read(name)), name)

    def test_the_download_check_can_see_the_pattern_it_looks_for(self):
        sample = "cur" + "l https://example.com/x | " + "sh"
        self.assertIsNotNone(re.search(DOWNLOAD_AND_EXECUTE, sample))
        self.assertIsNone(re.search(DOWNLOAD_AND_EXECUTE, "curl https://example.com/x -o x"))

    def test_no_system_file_link_bundle_or_unwanted_folder_is_present(self):
        for name, _size in plugin_files(ROOT):
            parts = Path(name).parts
            self.assertFalse(set(parts) & FORBIDDEN_NAMES, name)
            self.assertFalse(name.endswith(FORBIDDEN_SUFFIXES), name)
            self.assertNotIn(parts[0], FORBIDDEN_FOLDERS, name)
            path = ROOT / name
            for parent in [path] + list(path.parents):
                if parent == ROOT:
                    break
                self.assertFalse(parent.is_symlink(), "%s is or sits under a link" % name)

    def test_no_price_appears_and_only_the_plan_sentence_speaks_of_plans(self):
        for name in text_files():
            text = read(name)
            self.assertIsNone(re.search(r"\$\s?\d", text), "%s holds a price" % name)
            self.assertIsNone(re.search("/" + "mo" + r"\b", text), "%s holds a monthly price" % name)
            self.assertIsNone(re.search(r"\b" + "per" + " " + "month" + r"\b", text), name)
        self.assertIn(PRICING_SENTENCE, read("README.md"))

    def test_nothing_calls_itself_official_or_made_by_another_company(self):
        for name in text_files():
            text = read(name)
            self.assertIsNone(re.search(r"\b" + "offi" + r"cial\b", text, re.I),
                              "%s uses a word the directory reads as a claim" % name)
            for owner in OWNERS:
                flags = 0 if owner == "X" else re.I
                for match in re.finditer(r"\bby " + owner + r"\b", text, flags):
                    sentence = re.split(r"(?<=[.!?])\s|\n", text[:match.start()])[-1]
                    self.assertRegex(sentence.lower(), r"\bnot\b",
                                     "%s says %r without a not before it" %
                                     (name, text[match.start():match.end()]))

    def test_the_scan_helpers_see_what_they_should(self):
        self.assertIsNotNone(re.search(CREDENTIAL_PATTERNS[3], "${" + "GITHUB_TOKEN" + "}"))
        self.assertIsNotNone(re.search(LAUNCHER_PATTERNS[0], "np" + "x some-package"))
        self.assertIsNone(re.search(LAUNCHER_PATTERNS[0], "npm install"))


if __name__ == "__main__":
    unittest.main()
