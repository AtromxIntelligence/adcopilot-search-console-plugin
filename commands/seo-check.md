---
name: seo-check
description: A short SEO check of the customer's site from Search Console, with at most three findings and one proposed change.
---

Follow the `gsc-search-performance` skill for the 28-day read, then the `gsc-indexing` skill's sitemap read and an inspection of the two or three pages that earn the most clicks. `$ARGUMENTS` may name the site, a domain or an address. With none, use the one property `get_org_context` and `gsc_list_sites` show, or ask which when there are several.

Every `get_org_context` call here carries `source: "claude-plugin/adcopilot-search-console/0.1.0"`, sent exactly as written, version included. In a scheduled run with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing.

Answer once, in the shape the skills give: one headline line with the property and the dates read, at most three findings with their numbers, one recommendation as a proposal for a yes or a no, and what you could not see. Say how many pages you inspected, never that the site is indexed. A sitemap submit is proposed and sent only on an explicit yes. When Google Ads is connected, end by offering the `gsc-paid-vs-organic` skill, once, as a question.
