"""The manifests: .claude-plugin/plugin.json, .claude-plugin/marketplace.json and
.mcp.json, held to the values the plugin directory listing and the connector
dedupe rule depend on.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; CI runs it in checks.yml). Nothing here reads the environment.

Why .mcp.json is held byte-for-byte equal to one dict: every AdCopilot plugin
registers the same server under the same key with the same address. Claude
treats servers that point at the same address as one connection with one
sign-in, so a different key, a trailing slash or a query string would give a
customer who installs two AdCopilot plugins a second connector and a second
sign-in.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPO = "adcopilot-search-console-plugin"
NAME = "adcopilot-search-console"
DISPLAY_NAME = "AdCopilot for Google Search Console (SEO)"
OWNER = "Google"
DESCRIPTION_END = "Made by Atromx Intelligence, not by %s." % OWNER

FIELD_ORDER = [
    "name", "version", "description", "author", "homepage", "documentationUrl",
    "privacyPolicyUrl", "termsOfServiceUrl", "supportUrl", "repository",
    "license", "keywords", "displayName", "icon",
]
EXPECTED_MCP = {
    "mcpServers": {
        "adcopilot": {"type": "http", "url": "https://mcp.adcopilot.cloud/mcp"}
    }
}
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# The fields only the directory listing reads. A marketplace entry that carries
# one is reported by `claude plugin validate` as unknown.
LISTING_FIELDS = {
    "displayName", "keywords", "icon", "version", "license", "author",
    "homepage", "repository", "documentationUrl", "privacyPolicyUrl",
    "termsOfServiceUrl", "supportUrl",
}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def urls_in(value):
    """Every string in a JSON value that looks like an address."""
    if isinstance(value, str):
        return [value] if re.match(r"^[a-z]+://", value) else []
    if isinstance(value, dict):
        return [u for v in value.values() for u in urls_in(v)]
    if isinstance(value, list):
        return [u for v in value for u in urls_in(v)]
    return []


class PluginManifest(unittest.TestCase):

    def setUp(self):
        self.manifest = load(".claude-plugin/plugin.json")

    def test_fields_are_the_decided_set_in_the_decided_order(self):
        self.assertEqual(list(self.manifest.keys()), FIELD_ORDER)

    def test_name_is_a_valid_permanent_name(self):
        name = self.manifest["name"]
        self.assertEqual(name, NAME)
        self.assertRegex(name, NAME_PATTERN)
        self.assertTrue(name.startswith("adcopilot-"), name)

    def test_display_name_and_author_are_the_decided_strings(self):
        self.assertEqual(self.manifest["displayName"], DISPLAY_NAME)
        self.assertEqual(self.manifest["author"], {
            "name": "Atromx Intelligence", "url": "https://adcopilot.cloud"})

    def test_version_is_semver(self):
        self.assertRegex(self.manifest["version"], SEMVER)

    def test_description_leads_with_what_it_does_and_says_who_made_it(self):
        description = self.manifest["description"]
        self.assertTrue(description.endswith(DESCRIPTION_END), description)
        self.assertLessEqual(len(description), 600, len(description))
        first = description.split(".")[0]
        self.assertIn("SEO", first)
        self.assertIn("Search Console", first)

    def test_addresses_are_the_decided_ones(self):
        m = self.manifest
        self.assertEqual(m["homepage"], "https://adcopilot.cloud")
        self.assertEqual(m["documentationUrl"], "https://adcopilot.cloud/docs/")
        self.assertEqual(m["privacyPolicyUrl"], "https://adcopilot.cloud/privacy")
        self.assertEqual(m["termsOfServiceUrl"], "https://adcopilot.cloud/terms")
        self.assertEqual(m["supportUrl"],
                         "https://github.com/AtromxIntelligence/%s/issues" % REPO)
        self.assertEqual(m["repository"],
                         "https://github.com/AtromxIntelligence/%s" % REPO)
        self.assertEqual(m["license"], "MIT")

    def test_every_address_is_https(self):
        for path in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                     ".mcp.json"):
            for url in urls_in(load(path)):
                self.assertTrue(url.startswith("https://"), "%s: %s" % (path, url))

    def test_keywords_are_few_lowercase_kebab_case_and_unique(self):
        keywords = self.manifest["keywords"]
        self.assertLessEqual(len(keywords), 15)
        self.assertEqual(len(keywords), len(set(keywords)))
        for keyword in keywords:
            self.assertRegex(keyword, KEBAB)
        for expected in ("seo", "search-console", "adcopilot"):
            self.assertIn(expected, keywords)

    def test_icon_is_our_own_png(self):
        self.assertEqual(self.manifest["icon"], "./.claude-plugin/icon.png")
        icon = ROOT / ".claude-plugin" / "icon.png"
        self.assertTrue(icon.is_file())
        self.assertTrue(icon.read_bytes().startswith(PNG_MAGIC))
        # Text, so it would count toward the size limit; the mark is a PNG only.
        self.assertFalse((ROOT / ".claude-plugin" / "icon.svg").exists())

    def test_readme_version_paragraph_names_the_manifest_version(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        found = re.search(
            r"\*\*(\d+\.\d+\.\d+) \(\d{4}-\d{2}-\d{2}, written against AdCopilot "
            r"v\d+\.\d+\.\d+, live since \d{4}-\d{2}-\d{2}\)\*\*", readme)
        self.assertIsNotNone(found, "README has no version paragraph")
        self.assertEqual(found.group(1), self.manifest["version"])


class ConnectorRegistration(unittest.TestCase):

    def test_mcp_json_is_the_one_shared_registration(self):
        self.assertEqual(load(".mcp.json"), EXPECTED_MCP)

    def test_mcp_json_is_one_line_with_the_shared_text(self):
        text = (ROOT / ".mcp.json").read_text(encoding="utf-8")
        self.assertEqual(text.strip(), json.dumps(EXPECTED_MCP, separators=(",", ":")))


class Marketplace(unittest.TestCase):

    def setUp(self):
        self.market = load(".claude-plugin/marketplace.json")

    def test_it_names_the_repository_and_the_owner(self):
        self.assertEqual(self.market["name"], REPO)
        self.assertEqual(self.market["owner"], {
            "name": "Atromx Intelligence", "url": "https://adcopilot.cloud"})
        self.assertTrue(self.market["description"])

    def test_it_lists_this_plugin_from_the_repository_root_without_listing_fields(self):
        plugins = self.market["plugins"]
        self.assertEqual(len(plugins), 1)
        entry = plugins[0]
        self.assertEqual(entry["name"], NAME)
        self.assertEqual(entry["source"], "./")
        self.assertEqual(entry["category"], "Marketing")
        self.assertTrue(entry["description"])
        self.assertEqual(set(entry), {"name", "source", "description", "category"})
        self.assertEqual(set(entry) & LISTING_FIELDS, set())


if __name__ == "__main__":
    unittest.main()
