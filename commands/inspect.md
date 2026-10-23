---
name: inspect
description: Inspect one page's index status in Google, from Search Console's URL Inspection, and say what to do about it.
---

Follow the `gsc-indexing` skill for the page in `$ARGUMENTS`, a full address starting with `https://` or `http://`. If `$ARGUMENTS` is empty, ask for the address and wait. The page must sit under one of the customer's Search Console properties: find it with `gsc_list_sites`, and when none covers the address, say so and stop rather than inspecting under another site.

Every `get_org_context` call here carries `source: "claude-plugin/adcopilot-search-console/0.1.0"`, sent exactly as written, version included. In a scheduled run with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing.

Inspect the page once with `gsc_inspect_url`. Answer in plain words: Google's verdict and `coverageState` as Google words them, whether a robots.txt rule or a noindex rule stops it, which canonical Google chose against the one the page declares, whether Google could fetch it, and when Google last crawled it. Say it is the version Google holds, not the live page. Then the one remedy that fits, as the gsc-indexing skill sets it out. Do not call `gsc_request_indexing` unless the page carries JobPosting or BroadcastEvent markup and the customer says yes. One inspection says nothing about the rest of the site, and the answer says so.
