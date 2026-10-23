---
name: gsc-search-performance
description: Show which searches and pages earn clicks on Google, from the customer's own Search Console data, including queries that nearly rank, click-through gaps, brand versus non-brand and country or device splits. Use when someone asks about SEO, organic traffic, keywords they rank for, search queries, impressions, click-through rate, average position, why a page gets few clicks, or what to write about next.
---

# Search performance

The customer wants to know what Google Search already does for their site: which searches bring them clicks, which pages earn them, and where a small change could earn more. AdCopilot reads their own Search Console for this, through the connector at `https://mcp.adcopilot.cloud/mcp`. It reads no rank tracker and no other search engine.

## Start

Call `get_org_context` first, before any other tool, with `source: "claude-plugin/adcopilot-search-console/0.1.0"`. Send `source` exactly as written, version included: it tells AdCopilot that this plugin is installed here. If this run is a scheduled task with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing. This plugin sets up no schedule.

`get_org_context`'s `next_step` and `playbook` describe the whole workspace, not this request. Do this request as written here, keep any limit `next_step` adds, and offer the rest afterwards.

If Search Console is not connected, say what connecting it unlocks, in the server's own words (`unlocks`) and with the connect link it gives, never an address from memory, and stop. Invent nothing about a site you cannot read.

## What this reads

`gsc_list_sites` and `gsc_search_analytics`. When Google Ads is also connected, `list_accessible_customers` and `get_keyword_metrics`, for Google's monthly search counts only. Every number you give is a number a tool returned. Never estimate, round up or invent one, and when a read fails or comes back empty, say so.

## The sequence

1. **Which property.** `gsc_list_sites`, then pass the exact `siteUrl` it returns. A domain property (`sc-domain:example.com`) and a URL-prefix property (`https://www.example.com/`) are different sites with different numbers. If several are listed and the customer has not said which, ask once.
2. **The window.** 28 days ending three days before today, as `start_date` and `end_date` in YYYY-MM-DD. Search Console's finished data runs two to three days behind, and Google counts each day in California time (both from Google's help, checked 23 October 2026). The newest days come back as absent rows, not zeros, so a seven-day window is really four or five days of data. Say which dates you read.
3. **Queries and pages.** `gsc_search_analytics` with `dimensions: ["query"]`, then with `["page"]`. Pass `row_limit` yourself: the tool's default is 1,000, Google accepts 1 to 25,000 (checked 23 October 2026), and the tool cannot page on, so a big site comes back cut at the limit you asked for. When the rows returned equal the limit, say the list is cut and that any share you work out from it is a floor, not the figure.
4. **Country and device, when the question needs them.** `["query", "country"]` (country comes back as a three-letter code) or `["device"]`. Never read a site-wide average out as how the site does in one market: narrow it first.
5. **Queries that nearly rank.** Queries with real impressions and an average position of about 8 to 20. Say where you drew the line for "real", from this site's own numbers, and rank the list by impressions. For each one worth a change, check whether the page that should answer it ever says what people typed. AdCopilot cannot fetch a page, so use this client's own web-fetch tool where it has one, and otherwise ask the customer for the page's title, its main heading and its first sentence. Never describe a page's wording you have not read.
6. **Click-through gaps.** Pages or queries that sit near the top but earn few clicks, or that show many impressions and few clicks. Compare them with this site's other pages, never with a benchmark figure from memory. The usual lever is the page's title and description. Draft new ones as your own work, say that AdCopilot read no page to write them, and leave the edit to the customer: this plugin changes no page.
7. **Brand and non-brand.** Search Console has no brand flag. Ask which terms are the brand, or split on the site's own name and say that you did. Report the two apart, because a brand click is someone who already knew the site.
8. **Search volumes, only when Google Ads is connected.** Call `list_accessible_customers` for the `customer_id`, and ask which account if there are several. Then call `get_keyword_metrics` once, with the few queries you are discussing and not every row, to add how many people search each one a month. Those are Google's own estimates for a location and language, and the answer says which. A blank means too few to report, not none. One call, never a loop. When Google Ads is not connected, say volumes need it and go on without them.

## Reading the numbers

- **Impressions are appearances, not demand.** A page can take many impressions at position 40 to 90 and earn nothing. Look at clicks and position before calling any page a performer.
- **Average position is an average, not a rank.** Google defines it for a site as the average position of the topmost result from the site (checked 23 October 2026). A site can show a good average for its own name and appear nowhere on page one for the searches that matter. To say where it stands in one country, read that country and say it is still an average.
- **A row exists only for a search where the site was shown.** The data cannot say where people searched and did not see the site.
- **Search Console leaves rows out.** It does not track queries made very few times or that carry personal or sensitive information, and it keeps top rows rather than all rows (checked 23 October 2026). Query rows therefore add up to less than page rows.
- **Search Console clicks are not Google Analytics sessions.** Never mix the two in one figure.

## The answer

One headline line: the property, the dates you read, and the clicks, impressions and click-through rate. Then at most three findings, biggest first, each with its numbers and what they mean in plain words. Then one recommendation, as a proposal the customer can answer yes or no to: the page or query, the change, what doing it costs (usually an edit) and what leaving it costs in the clicks at stake. Then what you could not see.

## What AdCopilot cannot see here

Where a search ranks right now, searches where the site was not shown, any search engine but Google, competitors, Core Web Vitals (the `gsc-page-experience` skill says what it can do), manual actions, and a site-wide count of indexed pages. Say which of these the question needed.

## Changes

Every change is proposed first and applied only on the customer's explicit yes in this conversation. A proposal says what it changes and how to undo it. Nothing is ever deleted. This skill makes no change in Search Console.

## What breaks

Reporting average position as a rank. Calling a high-impression page a good page. Turning rows into a verdict such as "Google shows you at the top". Reading a truncated list as the whole site. Describing a page you have not read. Each reads as a confident answer and sends the customer the wrong way.

## What is next

Offer, in this order: the one page edit you found; the `gsc-indexing` skill for any page that earns nothing; and, when Google Ads is connected, the `gsc-paid-vs-organic` skill.
