---
name: gsc-paid-vs-organic
description: Compare the searches a Google Ads account pays for with the searches the same site already ranks for in Search Console, over the same dates, to find paid clicks organic may already cover and searches worth testing as ads. Reads only. Use when someone asks whether they pay for searches they already rank for, about paid versus organic, cannibalization, or which organic queries they never bid on. Needs Google Ads and Search Console both connected.
---

# Paid against organic

The customer wants to know whether they are paying for searches the site already wins for free, and which searches the site wins that they never advertise on. AdCopilot sets the Google Ads search terms beside the site's Search Console queries, over the same dates, through the connector at `https://mcp.adcopilot.cloud/mcp`.

## Start

Call `get_org_context` first, before any other tool, with `source: "claude-plugin/adcopilot-search-console/0.1.0"`. Send `source` exactly as written, version included: it tells AdCopilot that this plugin is installed here. If this run is a scheduled task with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing. This plugin sets up no schedule.

`get_org_context`'s `next_step` and `playbook` describe the whole workspace, not this request. Do this request as written here, keep any limit `next_step` adds, and offer the rest afterwards.

This needs two products. If Google Ads or Search Console is not connected, say what connecting it unlocks, in the server's own words (`unlocks`) and with the connect link it gives, never an address from memory, and stop. Invent nothing about an account or a site you cannot read.

## What this reads

`list_accessible_customers` for the `customer_id`, asking which account if there is more than one and never choosing for the customer, then `paid_vs_organic` with that `customer_id`. It takes `site_url` (when the answer says it needs one, because several sites are connected, ask the customer which of the sites it lists and call again), `days` (7 to 90, default 28) and `detail` (`summary` or `full`; start with `summary`). It reads Google Ads search terms and Search Console queries and changes nothing. Every number you give is a number it returned. Never estimate or invent one.

## How to read what comes back

- **Identical wording only.** Both sides are lower-cased, punctuation becomes a space, and there is no stemming and no fuzzy matching, so "shoe" is not "shoes". A pairing can be checked by eye. Say so when the customer asks why a term they expect is missing.
- **The buckets**, as the tool returns them: paid and ranking in the top three; paid and ranking lower; queries the site ranks in the top three for with no Google Ads search term found; the same for positions 4 to 20, which are the ones to test as ads; and paid terms with no Search Console row. Terms that contain the site's own name are counted and set aside. Report what the tool reports about them, and do not offer them as a saving: whether to pay for one's own name is a separate decision.
- **"No Search Console row" is not "no page."** Search Console leaves out rare queries, runs about three days behind, and reports an average position.
- **"No Google Ads search term found" is not "never advertised."** It means none in the search-term report, which hides low-volume terms and does not show Performance Max terms, so an ad may already run. The tool's notes say this, and so do you.
- **A cut list is said to be cut.** When the tool labels paid terms "not among the top 5,000 queries", say that and do not quote a count it withheld.
- **No Search Console read means no organic bucket.** When the tool could not read Search Console, nothing was compared. Say so and do not describe a bucket.
- **Money is the tool's, in the account's currency.** Name the currency `get_org_context` reports. When a field is in millionths (a `micros` field), divide by 1,000,000 once, and never print a micros number as money.

## The answer

One headline line: the site, the dates, how many paid search terms there were and what they cost, as the tool states them. Then at most three findings, biggest first, each with its terms and numbers:

- **Paid and already in the top three.** The paid click may be buying what the site would get anyway, or it may be adding to it: the data cannot say which. The way to find out is a test, such as pausing that one term for a stretch and watching total clicks, and a test is the customer's to decide.
- **Top-three queries with no ad.** Often fine, and often the cheapest result on the list. Say that they are free and that they are not a call to bid.
- **Positions 4 to 20 with no ad.** Candidates to test as ads. Whether they would win as ads is not something organic position shows.

Then one recommendation, as a proposal the customer can answer yes or no to, with what doing it costs and what leaving it costs, in the account's currency. Then what you could not see: how the paid and organic clicks interact, Performance Max terms, and rare queries.

## Changes

Every change is proposed first and applied only on the customer's explicit yes in this conversation. A proposal says what it changes and how to undo it. Nothing is ever deleted. This skill is read-only: it recommends and changes nothing, and a change to the Google Ads account is the customer's to ask for.

## What breaks

Calling a paid click wasted because the term also ranks organically. Treating a missing pairing as proof of a gap when the wording differed. Treating "no ad found" as "no ad". Quoting a cost without its currency. Offering a brand term as a saving.

## What is next

Offer, in this order: the one test worth running; the `gsc-search-performance` skill for the queries at positions 4 to 20, to see which page should answer each; and a repeat of this comparison a few weeks after any change, over the same number of days.
