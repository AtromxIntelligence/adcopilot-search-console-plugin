---
name: gsc-page-experience
description: Check page experience as far as Search Console shows it to AdCopilot, which means mobile versus desktop clicks and position, how Google crawled a page and which address it chose as canonical, plus a ranked fix list from a Core Web Vitals report the customer pastes. Use when someone asks about Core Web Vitals, page speed, mobile usability, mobile versus desktop traffic, HTTPS, rich results or page experience for SEO.
---

# Page experience

The customer wants to know whether the way their pages load and display is costing them search clicks. Say first what AdCopilot can and cannot read for this, then do the part it can, through the connector at `https://mcp.adcopilot.cloud/mcp`.

## Start

Call `get_org_context` first, before any other tool, with `source: "claude-plugin/adcopilot-search-console/0.1.0"`. Send `source` exactly as written, version included: it tells AdCopilot that this plugin is installed here. If this run is a scheduled task with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing. This plugin sets up no schedule.

`get_org_context`'s `next_step` and `playbook` describe the whole workspace, not this request. Do this request as written here, keep any limit `next_step` adds, and offer the rest afterwards.

If Search Console is not connected, say what connecting it unlocks, in the server's own words (`unlocks`) and with the connect link it gives, never an address from memory, and stop. Invent nothing about a site you cannot read.

## What AdCopilot cannot read today, said first

AdCopilot cannot read Core Web Vitals or Search Console's HTTPS report today. Search Console's API has no call for either (its methods are search analytics, sitemaps, sites and URL inspection, checked 23 October 2026), and AdCopilot reads Search Console through that API. Say this plainly, once and near the top of the answer, whenever the question needs either. What the customer pastes from those reports is the only way they enter the answer, and AdCopilot did not measure it.

## What this reads

`gsc_list_sites`, `gsc_search_analytics` and `gsc_inspect_url`. Every number you give is a number a tool returned or one the customer pasted, and you say which. Never estimate, round up or invent one.

## The sequence

1. **Which property.** `gsc_list_sites`, then pass the exact `siteUrl` it returns. If several are listed and the customer has not said which, ask once.
2. **Mobile against desktop.** `gsc_search_analytics` over 28 days ending three days before today (Search Console's finished data runs two to three days behind), with `dimensions: ["device"]` first. It returns clicks, impressions, click-through rate and average position for desktop, mobile and tablet. Then `["page", "device"]` for the pages that earn the most clicks, with `row_limit` passed yourself, and say when a list is cut at the limit. Compare each page's mobile row with its own desktop row, never with a benchmark from memory. A gap in position or click-through between the two is a lead, not a verdict: the people searching on a phone are not the same people, or the same searches, as on a desktop.
3. **How Google crawled the pages that matter.** `gsc_inspect_url` with `inspectionUrl` and `siteUrl`, for the few pages that earn the most. Report `crawledAs` (Google's primary crawler for the page, mobile or desktop), `googleCanonical` against `userCanonical`, `pageFetchState`, and the rich-results result when the answer carries one. A missing rich-results result means Google found none for that page, not that something failed. Say these describe the version Google holds, not the live page. Google has deprecated the mobile-usability result in its API (checked 23 October 2026), so report no mobile-usability verdict.
4. **HTTPS, as far as it goes.** Whether the page's address and the canonical Google chose start with `https` shows which version Google holds. It does not replace Search Console's HTTPS report, which AdCopilot cannot read. Say both halves.
5. **Core Web Vitals, from what the customer pastes.** Ask them to open Search Console's Core Web Vitals report, which Google builds from real visitors' data on three measures (LCP, INP and CLS) and groups by status (Poor, Need improvement, Good) and by groups of similar URLs (checked 23 October 2026), or to run PageSpeed Insights on a page, and to paste what it says. Read only what they paste. A group's status describes a group, not each URL in it, so say that. Then rank what to fix first by the clicks at stake: match the pasted URLs to the page clicks from step 2, and say that the clicks are the window's clicks for those pages. Where a pasted URL has no row, say it earned no clicks in the window. Never invent a score, a threshold or a pass mark: the report's own status is the referee.

## The answer

One headline line: the property, the dates read, and how clicks split between mobile and desktop. Then at most three findings, biggest first, each with its numbers. Then one recommendation as a proposal, with what doing it costs and what leaving it costs in the clicks at stake. Then what you could not see: Core Web Vitals and the HTTPS report unless the customer pasted them, and anything on the live page.

## Changes

Every change is proposed first and applied only on the customer's explicit yes in this conversation. A proposal says what it changes and how to undo it. Nothing is ever deleted. This skill changes nothing in Search Console and nothing on the site. Fixes to a page belong to the customer or their developer, and your guidance on them is advice, not something AdCopilot applies.

## What breaks

Reporting a Core Web Vitals result nobody pasted. Treating a group's status as one page's. Reading a mobile gap as proof of a speed problem. Reporting a mobile-usability verdict the API no longer gives. Saying "HTTPS is fine" from an address alone.

## What is next

Offer, in this order: the one page fix with the most clicks behind it; the `gsc-indexing` skill for any page whose inspection showed a problem; and a second look once the customer pastes the Core Web Vitals report again after a fix.
