# AdCopilot for Google Search Console (SEO)

SEO, Search Console, keywords, indexing and page experience from your AI client. AdCopilot reads your Google Search Console and shows which searches and pages earn clicks, the queries you nearly rank for, why a page is or is not indexed, whether Google reads your sitemap, and how mobile and desktop compare. It proposes any change first, such as submitting a sitemap, and makes it only on your yes.

What works today, in full, through the AdCopilot connector:

- **Search performance.** Which queries and pages earn clicks, by country and device (`gsc_search_analytics`): queries you nearly rank for (average position about 8 to 20), click-through gaps, and brand against non-brand. With Google Ads connected it adds Google's monthly search counts for the queries it names (`get_keyword_metrics`), labelled as estimates.
- **Indexing and sitemaps.** Why a page is or is not indexed, in Google's own words, from `gsc_inspect_url`, sampled across your page families and never claimed for the whole site; and whether Google reads your sitemap, from `gsc_list_sitemaps`. A sitemap submit with `gsc_submit_sitemap` is proposed first and sent only on your yes.
- **Page experience, as far as Search Console shows it.** Mobile against desktop clicks, click-through and position, and how Google crawled a page and which canonical it chose.
- **Paid against organic.** With Google Ads connected too, the searches you pay for that you already rank for, and the ones you rank for and never advertise on, from `paid_vs_organic`. It only reads.

What AdCopilot cannot read today, and says so in every answer that needs it: Core Web Vitals and the HTTPS report (it reads what you paste from those reports), a site-wide count of indexed pages (it reads the export you paste from the Page indexing report), manual actions and security issues. Nothing in this plugin waits for a later connector, and this README promises nothing beyond the list above.

Made by Atromx Intelligence (https://adcopilot.cloud). Not affiliated with or endorsed by Google. Google and Google Search Console are trademarks of Google LLC. This plugin is not related to other products named AdCopilot.

The plugin is free (MIT). The AdCopilot connector is a hosted service: Free plan available; paid plans on https://adcopilot.cloud/pricing

## Install

Two steps on every surface: add the plugin, then sign in to the connector it brings.

### claude.ai, Cowork and the desktop app

1. Go to Customize, then Plugins, search for "AdCopilot for Google Search Console", and click Add.
2. Open the plugin's Connectors tab, click Connect beside `adcopilot`, and sign in.

The connector reports as missing until step 2. If you added AdCopilot by hand before, it is the same connector: Claude links a connector by its address.

### Claude Code

```
/plugin marketplace add AtromxIntelligence/adcopilot-search-console-plugin
/plugin install adcopilot-search-console@adcopilot-search-console-plugin
/mcp
```

The last step opens the connector list. Choose `adcopilot` and sign in. The plugin registers the connector at `https://mcp.adcopilot.cloud/mcp` for you. Claude Code puts the plugin's name in front of its commands, so they read `/adcopilot-search-console:setup` and so on.

### Then, on every surface

Signing in links your AdCopilot workspace, so you need an AdCopilot account. Your Google products are connected once, inside AdCopilot at https://app.adcopilot.cloud, not in your AI client, so a fresh sign-in can report nothing connected, which is the server answering correctly. Run `setup` first: it says what is connected.

## Already use another AdCopilot plugin?

There is one connector and one sign-in, whichever AdCopilot plugins you add. Every AdCopilot plugin points at the same address, so your AI client treats them as one connector. In Claude Code, `/mcp` shows the connector once, under whichever AdCopilot plugin loaded first. If Claude asks you to sign in again after you remove an AdCopilot plugin, run `/mcp` and sign in once.

## What you get

Three commands, which you type:

- `setup` checks the connector is connected and signed in, says whether Search Console is connected, and names the first thing to ask.
- `seo-check` gives a short read of your site: 28 days of searches, the sitemap and a sample of your top pages, with at most three findings and one proposed change.
- `inspect` takes one page's address and says what Google holds for it and what to do about it.

Four skills, which Claude draws on when the conversation calls for them:

- **gsc-search-performance** reads queries, pages, countries and devices, and Google's search counts when Google Ads is connected (`gsc_list_sites`, `gsc_search_analytics`, `list_accessible_customers`, `get_keyword_metrics`).
- **gsc-indexing** explains indexing verdicts and sitemap status, and proposes a sitemap submit (`gsc_list_sites`, `gsc_inspect_url`, `gsc_list_sitemaps`, `gsc_submit_sitemap`). It offers `gsc_request_indexing` only for job-posting and livestream pages, the only ones Google says its Indexing API acts on.
- **gsc-page-experience** compares mobile with desktop, reads how Google crawled a page, and ranks fixes from a Core Web Vitals report you paste, by the clicks at stake (`gsc_list_sites`, `gsc_search_analytics`, `gsc_inspect_url`).
- **gsc-paid-vs-organic** compares your paid and organic searches (`list_accessible_customers`, `paid_vs_organic`).

Every skill starts with `get_org_context`, which tells AdCopilot this plugin is installed and what is connected.

## What it will not do

It will not change anything without your explicit yes in the conversation; each change is proposed first, with what it changes and how to undo it. It never deletes anything. It does not read Core Web Vitals, the HTTPS report, manual actions, security issues, other search engines or rank trackers. It schedules nothing, sends no email and changes no page on your site.

## Data

The plugin is instructions only: it runs no code and sends nothing anywhere itself. The AdCopilot connector at mcp.adcopilot.cloud reads and, on your yes, writes your Google products through Google's APIs with your Google sign-in. The [privacy policy](https://adcopilot.cloud/privacy) and the [terms](https://adcopilot.cloud/terms) say what it stores. The plugin holds no key, token or password and reads none from your machine.

## Support

- Something wrong with the plugin: [open an issue](https://github.com/AtromxIntelligence/adcopilot-search-console-plugin/issues).
- Something wrong with the connector (sign-in, a tool, your account): support@adcopilot.cloud.

## Version

**0.1.0 (2026-10-23, written against AdCopilot v2.44.0, live since 2026-10-22)** is the first release: three commands, four skills and the connector registration. Every tool name a skill uses was checked on 2026-10-23 against the connector's tool registry and its live tool list, and the Google facts the skills rely on against Google's own help and API pages the same day. The checks run for this release are the structural tests and `claude plugin validate --strict`. No model-driven evaluation was run, and the plugin has not yet been run in a real customer's conversation.

## Licence

MIT. Copyright Atromx Intelligence Private Limited. See [LICENSE](LICENSE).

## What CI runs

Two workflows run on every push to `main` and every pull request, and neither reads a secret. `checks.yml` runs `claude plugin validate --strict` (Claude Code installed from npm at a pinned version), checks that the JSON files parse and that every skill and command has a name and a description, runs the tests in `tests/` (manifest, front matter, real tool names only, the plugin marker, size limits, no credential reads, no package launchers), and checks that no download-and-execute pattern is present and the manifest version is not behind the latest tag. `leak-check.yml` runs gitleaks over every commit.
