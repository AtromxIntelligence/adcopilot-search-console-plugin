---
name: setup
description: Check the AdCopilot connector is connected and signed in, say whether Search Console is connected, and name the first thing to ask.
---

Open the first answer with what works today, in these words: AdCopilot reads your Search Console through its connector today. That is which searches and pages earn clicks, why a page is or is not indexed, whether Google reads your sitemap, and how mobile and desktop compare, with a sitemap submit proposed first and sent only on your yes. When Google Ads is connected too, it also compares the searches you pay for with the ones you already rank for, and adds Google's monthly search counts. What it cannot read today: Core Web Vitals, the HTTPS report, manual actions, security issues and a site-wide count of indexed pages. For the first two and the last it reads what you paste from Search Console's own reports, and for manual actions and security issues it can only point you to those two reports. Nothing in this plugin waits for a later connector.

Then call `get_org_context` with `source: "claude-plugin/adcopilot-search-console/0.1.0"`, before any other tool. Send `source` exactly as written, version included. If this run is a scheduled task with nobody there to answer, send `source: "claude-scheduled"` instead and change nothing. This plugin sets up no schedule.

Read what it says is connected and say it in a few lines: Search Console first, then, only as context, Google Ads, Google Analytics 4 and Google Tag Manager, since this plugin works with Search Console and, for one comparison, Google Ads.

- **Search Console is connected.** Say so, name the sites `get_org_context` reports, and go to the last step.
- **Search Console is not connected.** Say what connecting it unlocks, in the server's own words (`unlocks`) and with the connect link `get_org_context` gives, never an address from memory. Google products are connected once, inside AdCopilot, not in this AI client: a fresh sign-in that reports nothing connected is the server answering correctly, not a fault. Then stop.
- **The tools are missing, or the connector asks to sign in.** A missing tool proves nothing, because the tool list can be out of date, so believe what `get_org_context` says. If it cannot be called, the connector is not signed in. In Claude Code, run `/mcp`, choose `adcopilot` and sign in. In claude.ai, Cowork and the desktop app, open this plugin from the plugin list, open its Connectors tab, choose Connect beside `adcopilot` and sign in. If a tool is still missing after signing in, `/mcp`, choose `adcopilot`, then Reconnect refetches the tool list in Claude Code (at the time of writing); reinstalling the plugin is the last resort.
- **They have another AdCopilot plugin installed, or added or removed one.** There is one connector and one AdCopilot account whichever AdCopilot plugins are added. In Claude Code, `/mcp` lists it once, under whichever AdCopilot plugin loaded first, and the sign-in belongs to that entry. If Claude asks for a sign-in again after an AdCopilot plugin was added or removed, run `/mcp` and sign in once.

End with the one next step: the `seo-check` command, which gives a short read of the site, and the question it answers. Do not offer anything else.
