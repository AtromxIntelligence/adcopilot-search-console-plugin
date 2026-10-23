"""The plugin's own text: every skill and command parses, names only tools the
connector really has, sends the plugin marker the server reads, and carries the
approval rule. Nothing here reads the environment, and nothing needs a model.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; CI runs it in checks.yml).

Why each rule exists:

* Front matter. A skill or command whose front matter does not parse, or whose
  description is not one text value, is blocked by the plugin directory, and one
  that loses its name stops being found. There is no YAML parser in the standard
  library, so the check reads the one shape these files use (single-line
  `key: value`) and refuses what a YAML reader would also refuse in a plain
  value: a colon followed by a space, or a space and a hash.
* Tool names. A skill that names a tool the connector does not serve sends the
  customer a promise nobody keeps. `connector_tools.txt` is the connector's
  registry; three tools the live connector does not serve today are refused by name.
* Bare names. The long namespaced form of a tool name, which carries the plugin's
  own name, belongs to whichever AdCopilot plugin Claude Code loaded first, so a
  skill that wrote it out would be wrong for anyone who has two AdCopilot plugins.
* The marker. `get_org_context` is told `claude-plugin/<plugin name>/<version>`.
  The server reads a value that starts `claude-plugin/` as "a plugin is here"
  and a version it cannot read as "no version", so it never hands the turn to
  the main plugin's skills, which are not installed here. The bare word, or
  `claude-plugin/<version>` alone, would say otherwise.
"""

import json
import re
import unittest
from pathlib import Path

from test_plugin_size import plugin_files

ROOT = Path(__file__).resolve().parents[1]

NAME = "adcopilot-search-console"
IS_PLATFORM_PLUGIN = False  # a platform plugin also carries a today/later sentence
OWNER_MARKS = "Google and Google Search Console are trademarks of Google LLC."
TRADEMARK_LINE = ("Not affiliated with or endorsed by Google. " + OWNER_MARKS)
MADE_BY_LINE = "Made by Atromx Intelligence (https://adcopilot.cloud)."
UNRELATED_LINE = "This plugin is not related to other products named AdCopilot."
PRICING_LINE = ("The plugin is free (MIT). The AdCopilot connector is a hosted "
                "service: Free plan available; paid plans on "
                "https://adcopilot.cloud/pricing")
APPROVAL = ("Every change is proposed first and applied only on the customer's "
            "explicit yes in this conversation.")
UNDO = "A proposal says what it changes and how to undo it."
NO_DELETE = "Nothing is ever deleted."
UNCONNECTED = "say what connecting it unlocks"
# What this plugin says it cannot read, said in the README and by /setup.
CANNOT_READ = ["Core Web Vitals", "HTTPS report", "manual actions",
               "security issues", "site-wide count"]
# Tools the live connector does not serve today, or refuses for every caller.
NOT_SERVED = {
    "shopping_product_issues", "lsa_leads", "lsa_rate_lead", "remove_ad",
    "remove_keyword", "remove_campaign_asset", "remove_asset_from_asset_group",
}
# A backticked token that starts like a tool must be one.
TOOL_PREFIXES = ("gsc_", "ga4_", "gtm_", "get_", "list_", "create_", "update_",
                 "set_", "add_", "remove_", "pause_", "attach_", "link_",
                 "analyze_", "save_", "submit_", "inspect_", "request_")


def read(path):
    return Path(path).read_text(encoding="utf-8")


def flat(text):
    """Text with every run of whitespace as one space, so a rule written across
    two lines is still found."""
    return re.sub(r"\s+", " ", text)


def connector_tools():
    names = set()
    for line in read(ROOT / "tests" / "connector_tools.txt").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.add(line)
    return names


def split_front_matter(text):
    """(front matter lines, body) or raise ValueError."""
    if not text.startswith("---\n"):
        raise ValueError("no front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("front matter is not closed")
    return text[4:end].split("\n"), text[end + 5:]


def parse_front_matter(text):
    lines, body = split_front_matter(text)
    fields = {}
    for line in lines:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*): (.+)$", line)
        if not match:
            raise ValueError("not a single-line `key: value`: %r" % line)
        key, value = match.groups()
        if key in fields:
            raise ValueError("duplicate key %r" % key)
        fields[key] = value.strip()
    return fields, body


def plain_value_problem(value):
    """Why a YAML reader would not take `value` as one plain text value, or None."""
    if value[0] in "[{|>*&!%@`'\"#-?:,":
        return "starts with %r" % value[0]
    if ": " in value:
        return "holds a colon and a space"
    if " #" in value:
        return "holds a space and a hash"
    if value.endswith(":"):
        return "ends with a colon"
    return None


def skills():
    return sorted((ROOT / "skills").glob("*/SKILL.md"))


def commands():
    return sorted((ROOT / "commands").glob("*.md"))


def tool_like(token):
    return token.startswith(TOOL_PREFIXES) or token in NOT_SERVED


def backticked_tokens(text):
    return re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", text)


class FrontMatter(unittest.TestCase):

    def test_there_are_skills_and_commands_in_the_expected_numbers(self):
        self.assertTrue(3 <= len(skills()) <= 5, len(skills()))
        self.assertTrue(1 <= len(commands()) <= 3, len(commands()))

    def test_every_skill_and_command_has_a_name_and_one_text_description(self):
        for path in skills() + commands():
            fields, body = parse_front_matter(read(path))
            self.assertEqual(set(fields), {"name", "description"}, path)
            expected = path.parent.name if path.name == "SKILL.md" else path.stem
            self.assertEqual(fields["name"], expected, path)
            description = fields["description"]
            self.assertTrue(description, path)
            self.assertIsNone(plain_value_problem(description),
                              "%s: description %s" % (path, plain_value_problem(description)))
            self.assertTrue(body.strip(), "%s has no body" % path)

    def test_skill_names_are_this_plugins_own_and_never_a_main_plugin_name(self):
        names = [p.parent.name for p in skills()]
        self.assertEqual(len(names), len(set(names)))
        for name in names:
            self.assertTrue(name.startswith("gsc-"), name)
            self.assertNotIn(name, {"adcopilot-seo", "adcopilot-meta"})

    def test_the_front_matter_check_refuses_what_a_yaml_reader_refuses(self):
        for bad in ("Use when: a page is gone", "a page # not a comment", "[a, b]",
                    "'quoted'", "ends with a colon:"):
            self.assertIsNotNone(plain_value_problem(bad), bad)
        self.assertIsNone(plain_value_problem("Find out why a page is not indexed."))
        with self.assertRaises(ValueError):
            parse_front_matter("---\nname: a\ndescription:\n  - x\n---\nbody\n")
        with self.assertRaises(ValueError):
            parse_front_matter("name: a\n")


class ToolNames(unittest.TestCase):

    def test_every_tool_a_skill_or_command_names_is_one_the_connector_serves(self):
        served = connector_tools()
        self.assertIn("get_org_context", served)
        for path in skills() + commands():
            for token in backticked_tokens(read(path)):
                if tool_like(token):
                    self.assertIn(token, served, "%s names %s" % (path, token))
                    self.assertNotIn(token, NOT_SERVED, "%s names %s" % (path, token))

    def test_the_registry_file_leaves_the_switched_off_tools_out(self):
        self.assertEqual(connector_tools() & NOT_SERVED, set())

    def test_no_namespaced_tool_name_appears_anywhere(self):
        needle = "mcp__" + "plugin_"
        for name, _size in plugin_files(ROOT):
            if name.endswith(".png") or name == "tests/connector_tools.txt":
                continue
            self.assertNotIn(needle, read(ROOT / name), name)

    def test_each_skill_calls_get_org_context_before_any_other_tool(self):
        for path in skills():
            text = read(path)
            first = text.find("`get_org_context`")
            self.assertGreaterEqual(first, 0, path)
            for match in re.finditer(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", text):
                if tool_like(match.group(1)) and match.group(1) != "get_org_context":
                    self.assertGreater(match.start(), first,
                                       "%s names %s first" % (path, match.group(1)))
                    break


class PluginMarker(unittest.TestCase):

    def setUp(self):
        self.version = json.loads(read(ROOT / ".claude-plugin" / "plugin.json"))["version"]
        self.marker = "claude-plugin/%s/%s" % (NAME, self.version)

    def test_every_file_that_calls_get_org_context_sends_the_plugin_marker(self):
        for path in skills() + commands():
            text = read(path)
            if "get_org_context" in text:
                self.assertIn('source: "%s"' % self.marker, text, path)

    def test_the_marker_is_never_bare_and_never_a_main_plugin_version(self):
        for path in skills() + commands():
            text = read(path)
            for match in re.finditer(r"claude-plugin", text):
                tail = text[match.start():match.start() + len(self.marker)]
                self.assertEqual(tail, self.marker,
                                 "%s: `claude-plugin` is not followed by /%s/%s" %
                                 (path, NAME, self.version))
            self.assertNotRegex(text, r"claude-plugin/\d")

    def test_a_scheduled_run_is_told_to_send_the_scheduled_source_and_change_nothing(self):
        for path in skills() + commands():
            text = flat(read(path))
            if "get_org_context" in text:
                self.assertIn('send `source: "claude-scheduled"` instead and change nothing',
                              text, path)

    def test_no_component_sets_up_a_schedule(self):
        for path in skills() + commands():
            self.assertNotRegex(read(path).lower(), r"/schedule\b|cron|routine\.schedule", path)


class SkillRules(unittest.TestCase):

    def test_every_skill_holds_the_approval_paragraph(self):
        for path in skills():
            text = flat(read(path))
            self.assertIn(APPROVAL, text, path)
            self.assertIn(UNDO, text, path)
            self.assertIn(NO_DELETE, text, path)

    def test_every_skill_says_what_to_do_when_search_console_is_not_connected(self):
        for path in skills():
            text = flat(read(path))
            self.assertIn(UNCONNECTED, text, path)
            self.assertIn("`unlocks`", text, path)
            self.assertIn("never an address from memory", text, path)

    def test_every_skill_keeps_the_next_step_in_its_place(self):
        for path in skills():
            text = flat(read(path))
            self.assertIn("`next_step` and `playbook` describe the whole workspace, "
                          "not this request", text, path)

    def test_skills_that_read_search_console_state_the_dates_they_read(self):
        for name in ("gsc-search-performance", "gsc-page-experience"):
            text = flat(read(ROOT / "skills" / name / "SKILL.md"))
            self.assertIn("28 days ending three days before today", text, name)
            self.assertIn("row_limit", text, name)

    def test_skills_that_state_a_google_fact_date_it(self):
        for path in skills():
            text = flat(read(path))
            if "Google's help" in text or "Google's own documentation" in text:
                self.assertIn("checked 23 October 2026", text, path)

    def test_the_skills_say_what_they_cannot_see(self):
        needs = {
            "gsc-search-performance": ["Core Web Vitals", "manual actions"],
            "gsc-indexing": ["manual actions", "security issues", "site-wide"],
            "gsc-page-experience": ["Core Web Vitals", "HTTPS report"],
            "gsc-paid-vs-organic": ["Performance Max"],
        }
        for name, words in needs.items():
            text = read(ROOT / "skills" / name / "SKILL.md")
            for word in words:
                self.assertIn(word, text, "%s should mention %s" % (name, word))

    def test_the_indexing_skill_never_offers_request_indexing_for_an_ordinary_page(self):
        text = flat(read(ROOT / "skills" / "gsc-indexing" / "SKILL.md"))
        self.assertIn("Offer it only for those two kinds of page", text)
        self.assertIn("never report \"indexing requested\" as progress", text)

    def test_read_only_skills_say_they_change_nothing(self):
        self.assertIn("This skill is read-only",
                      flat(read(ROOT / "skills" / "gsc-paid-vs-organic" / "SKILL.md")))


class Readme(unittest.TestCase):

    def setUp(self):
        self.text = read(ROOT / "README.md")

    def outside_fences(self):
        return re.sub(r"```.*?```", "", self.text, flags=re.S)

    def test_it_has_more_than_the_directorys_forty_words_outside_code(self):
        words = len(re.findall(r"\S+", self.outside_fences()))
        self.assertGreater(words, 40)
        self.assertTrue(600 <= words <= 1200, words)

    def test_it_holds_the_trademark_line_and_the_who_made_it_lines(self):
        text = flat(self.text)
        self.assertIn(MADE_BY_LINE, text)
        self.assertIn(TRADEMARK_LINE, text)
        self.assertIn(UNRELATED_LINE, text)
        self.assertIn(PRICING_LINE, text)

    def test_it_holds_the_install_steps_for_every_surface(self):
        text = self.text
        self.assertIn("/plugin marketplace add AtromxIntelligence/adcopilot-search-console-plugin", text)
        self.assertIn("/plugin install adcopilot-search-console@adcopilot-search-console-plugin", text)
        self.assertIn("Connectors tab", text)
        self.assertIn("https://app.adcopilot.cloud", text)

    def test_it_holds_the_one_connector_one_sign_in_answer(self):
        text = flat(self.text)
        self.assertIn("Already use another AdCopilot plugin?", text)
        self.assertIn("There is one connector and one AdCopilot account, whichever "
                      "AdCopilot plugins you add.", text)
        self.assertIn("If Claude asks you to sign in again after you add or remove an "
                      "AdCopilot plugin, run `/mcp` and sign in once.", text)

    def test_it_says_what_it_cannot_read_and_discloses_the_connector(self):
        text = flat(self.text)
        for phrase in CANNOT_READ:
            self.assertIn(phrase, text, phrase)
        self.assertIn("The plugin is instructions only: it runs no code and sends "
                      "nothing anywhere itself.", text)
        self.assertIn("mcp.adcopilot.cloud", text)
        self.assertIn("https://adcopilot.cloud/privacy", text)

    def test_setup_says_the_same_things_in_its_first_answer(self):
        text = flat(read(ROOT / "commands" / "setup.md"))
        for phrase in CANNOT_READ:
            self.assertIn(phrase, text, phrase)
        self.assertIn("Nothing in this plugin waits for a later connector.", text)
        self.assertIn("Open the first answer with what works today", text)

    def test_it_names_every_skill_and_command_it_ships(self):
        for path in skills():
            self.assertIn("**%s**" % path.parent.name, self.text, path)
        for path in commands():
            self.assertIn("`%s`" % path.stem, self.text, path)

    def test_it_has_the_sections_the_ship_script_and_the_reader_need(self):
        for heading in ("## Install", "## What you get", "## What it will not do",
                        "## Data", "## Support", "## Version", "## Licence",
                        "## What CI runs"):
            self.assertIn("\n" + heading + "\n", self.text, heading)


if __name__ == "__main__":
    unittest.main()
