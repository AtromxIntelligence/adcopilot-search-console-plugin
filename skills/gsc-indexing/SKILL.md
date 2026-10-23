---
name: gsc-indexing
description: Find out why a page is or is not indexed in Google, from Search Console's URL Inspection, and whether Google reads the sitemap, with a sampled verdict per page and never a claim about the whole site. Use when someone asks why a page is not showing in Google, is not indexed, is discovered or crawled but not indexed, whether a sitemap is working, how to submit a sitemap, or how to get a page indexed.
---

# Indexing and sitemaps

The customer wants to know why Google does or does not hold a page, and whether it reads their sitemap. AdCopilot answers from their own Search Console, through the connector at `https://mcp.adcopilot.cloud/mcp`.

## Start

Call `get_org_context` first, before any other tool, with `source: "claude-plugin/adcopilot-search-console/0.1.0"`. Send `source` exactly as written, version included: it tells AdCopilot that this plugin is installed here. If this run is a scheduled task with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing. This plugin sets up no schedule.

`get_org_context`'s `next_step` and `playbook` describe the whole workspace, not this request. Do this request as written here, keep any limit `next_step` adds, and offer the rest afterwards.

If Search Console is not connected, say what connecting it unlocks, in the server's own words (`unlocks`) and with the connect link it gives, never an address from memory, and stop. Invent nothing about a site you cannot read.

## Five tools, and what they cannot do

`gsc_list_sites`, `gsc_list_sitemaps` and `gsc_inspect_url` read. `gsc_submit_sitemap` and `gsc_request_indexing` write, so both are proposed first and sent only on an explicit yes. Every number you give is a number a tool returned.

The gaps matter more than the tools:

- **There is no site-wide list of pages Google has not indexed, and no count.** `gsc_inspect_url` gives one URL's verdict. For a site-wide picture, ask the customer to open Search Console's Page indexing report, use its export button (Google's help says many reports have one, checked 23 October 2026), and paste or attach what they get. Read that, and until they do say you checked a handful of pages, not the site.
- **An inspection shows the version Google holds, not the live page.** Google's own documentation says only the status of the version in the Google index is available through the API and that a live URL cannot be tested there (checked 23 October 2026). After the customer edits a page, `lastCrawlTime` says whether Google has fetched the new version yet. Search Console's own URL Inspection tool has an "Inspect a live URL" task for the live page, which the customer runs there.
- **Manual actions and security issues are not readable.** They are separate Search Console reports (the Manual actions report and the Security issues report). Never say a site has no penalty or is not flagged. Say you cannot see either, and that the customer should open those two reports.
- **The sitemap list has a dead column.** `gsc_list_sitemaps` returns an `indexed` count per content type, and Google marks that field "Deprecated; do not use" (checked 23 October 2026). It is never evidence of an indexing problem. Only the Page indexing report or `gsc_inspect_url` says whether something is indexed.

## The sequence

1. **Which property.** `gsc_list_sites`, then pass the exact `siteUrl` it returns, domain property or URL-prefix property as listed. If several are listed and the customer has not said which, ask once.
2. **Is the sitemap read.** `gsc_list_sitemaps`: each sitemap's path, when it was last submitted and last downloaded, whether it is still pending, its errors and warnings, and how many URLs it holds by type. Say what Google reports about the sitemap itself, ignore the `indexed` column, and when no sitemap is listed say so and propose submitting one.
3. **Inspect a sample.** `gsc_inspect_url` with `inspectionUrl` and `siteUrl` for a handful of pages across the site's page families: a key page, a blog or help page, a product or service page, a recently added page. Say which pages you checked, and that one inspection says nothing about the rest. Read the whole result, not just the crawl date: the `verdict`, `coverageState` in Google's own words, `robotsTxtState`, `indexingState`, `pageFetchState`, `googleCanonical` against `userCanonical`, `lastCrawlTime`, and any sitemaps and referring URLs it lists. A field Google leaves out means Google has nothing to report, for example no canonical for a page it has not indexed.
4. **Match the remedy to the verdict.**
   - *Discovered, currently not indexed.* Google found the URL and has not crawled it. Google's help says it usually wanted to crawl and expected that to overload the site, so it rescheduled (checked 23 October 2026). The remedies are fewer thin or near-duplicate URLs competing for the same crawl, links to the page from pages Google already crawls, an honest `lastmod` in the sitemap, and a server that answers quickly. Submitting the sitemap again changes nothing, because Google already has the URL.
   - *Crawled, currently not indexed.* Google read it and did not keep it, and its help says there is no need to resubmit (checked 23 October 2026). Google does not say why, so say so, and look at the page itself with the customer: whether it adds something a similar page on the site or elsewhere does not.
   - *Blocked by a noindex rule* (`indexingState` reports a meta tag or header). Someone told Google not to index it. If that is not intended, the customer removes the rule on the site.
   - *Disallowed by robots.txt* (`robotsTxtState`). A robots.txt rule stops Google fetching it. The customer changes the rule if that is not intended.
   - *Google chose a different canonical* (`googleCanonical` differs from `userCanonical`). Google treats the page as a copy of the one it chose. Say which, and whether that is what the customer meant.
   - *The page did not fetch* (`pageFetchState` is anything but successful). Name the state, such as not found, a server error or access denied, and what the customer's server or host should return instead.
   - *Indexed* (a passing verdict). Say when Google last crawled it, and when the customer is waiting for an edit to show, compare that date with the edit.
5. **Request indexing is almost never the answer.** `gsc_request_indexing` calls Google's Indexing API, which Google says can only be used to crawl pages with JobPosting, or BroadcastEvent embedded in a VideoObject (checked 23 October 2026). For any other page the call succeeds and Google does nothing with it, and the tool's own answer says indexing is not promised. Offer it only for those two kinds of page, run `gsc_inspect_url` on the page first, and never report "indexing requested" as progress. For an ordinary page the customer can use the Request indexing button in Search Console's URL Inspection tool by hand. Google's help says there is a daily limit on those requests and no guarantee the page appears (checked 23 October 2026).

## Changes

Every change is proposed first and applied only on the customer's explicit yes in this conversation. A proposal says what it changes and how to undo it. Nothing is ever deleted.

- **`gsc_submit_sitemap`.** Propose the exact sitemap address and the property it goes to. Submitting is additive and re-sending the same sitemap leaves the same state. To undo it, the customer deletes the sitemap in Search Console's Sitemaps report, and says so now: Google's help says deleting removes it from that report but Google will not forget the sitemap or the URLs in it (checked 23 October 2026). After a yes and the call, read `gsc_list_sitemaps` once and say what it shows. A just-submitted sitemap may still be pending. If Google refuses, say what Google said and do not retry in a loop.
- **`gsc_request_indexing`.** Only for the two kinds of page above, only on a yes. Afterwards say the notification was submitted, never that the page will be indexed.

## The answer

One headline line: the property, how many pages you inspected out of how many the customer has, and whether the sitemap is read. Then at most three findings, biggest first, each naming the page, Google's verdict in Google's words, and what it means in plain words. Then one recommendation as a proposal, with what doing it costs and what leaving it costs. Then what you could not see: the site-wide count, manual actions and security issues.

## What breaks

Telling a customer their pages are indexed on the strength of one inspection. Calling a page not indexed because of the sitemap's dead column. Offering to request indexing as though it worked. Promising a site has no penalty. Resubmitting a sitemap as the fix for a page Google has already discovered.

## What is next

Offer, in this order: the one change you found; a second look at the page a few days after the customer says an edit is live, since `lastCrawlTime` then says whether Google fetched the new version; the Page indexing report's export, so the next review can speak about the whole site; and the `gsc-search-performance` skill for the pages that are indexed and earn nothing.
