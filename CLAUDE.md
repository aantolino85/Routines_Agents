# Routines_Agents

Angelo's Claude Code agents. They live in one repo but are configured separately.

| Agent | Folder | Command | Schedule | Output |
|---|---|---|---|---|
| **Personal concierge** | `personal/` | `/weekend` | Wednesday 6:00pm ET | `personal/reports/YYYY-MM-DD.md` |
| **Professional deal desk** | `professional/` | `/deals` | Monday 7:40am ET | `professional/digests/YYYY-MM-DD.md` + `professional/data/deal_log.csv` |
| **Alternatives deal desk** (RIA lens) | `alternatives/` | `/alts` | Monday 7:10am ET | `alternatives/digests/YYYY-MM-DD.md` + `alternatives/data/deal_log.csv` |
| **Denver weekend** | `denver/` | `/denver` | Wednesday 5:20pm ET | `denver/reports/YYYY-MM-DD.md` |

## Routing
- For skiing, snow, nightlife, live music, trivia, dog events or the weekend, read `personal/CLAUDE.md` and follow it.
- For deals, energy, data centers, markets or policy, read `professional/CLAUDE.md` and follow it.
- For alternative investments (private equity, private credit, real assets, hedge funds, wealth-channel products) from an RIA's point of view, read `alternatives/CLAUDE.md` and follow it.
- For Denver, Boulder, Loveland or Fort Collins music and kid activities, read `denver/CLAUDE.md` and follow it.
- Never mix agents. Each report covers only its own topic; personal reports contain no work content, and deal digests contain no personal content.

## Subagents (`.claude/agents/`)
- `powder-scout`: snow forecasts and mountain ranking (personal)
- `nightlife-scout`: live music, trivia and other nights out near Andover (personal)
- `dog-scout`: dog meetups, events and boarding or daycare deals near Andover (personal)
- `deal-scout`: searches one coverage bucket of energy and data center news (professional; run several in parallel)
- `alts-scout`: searches one coverage bucket of alternative investment news (alternatives; run several in parallel)
- `denver-music-scout`: live music and nights out around Denver, Boulder, Loveland and Fort Collins (denver)
- `family-scout`: kid-friendly activities around Denver, Boulder, Loveland and Fort Collins (denver)

## House rules
- **Dates:** Always work out "this week" and "this weekend" from today's actual date (America/New_York).
- **Sources:** Every event, deal or claim needs a source link. Never invent events, venues, prices or deal terms. If something can't be verified, leave it out.
- **Committing:** After writing a report, commit it with a message like `personal: weekend report 2026-11-13` or `deals: digest 2026-11-16` and push to the current branch. Run `git pull --rebase` first, since other agents push to the same repo.
- **Publish the public page (after every report):** run `python3 site/build.py`, then publish the built page to that agent's artifact
  with the Artifact tool (load it with ToolSearch `select:Artifact`; action `publish`, the URL below, `file_path` = absolute path of the built file).
  Only republish that page, nothing else. If publishing fails, say so in the run summary; the report in the repo still counts.
  - Weekend Outlook → `site/out/weekend.html` → https://claude.ai/artifact/U8wvwagW6A9UJC2KSFaHPp
  - Deal Desk → `site/out/deals.html` → https://claude.ai/artifact/YQ9NUZeVt1penjzf8WdgRA
  - Alternatives Deal Desk → `site/out/alts.html` → https://claude.ai/artifact/CDDutzbMU1EsBhYSUx5ffV
  - Denver Weekend → `site/out/denver.html` → https://claude.ai/artifact/2jHrZf4CrX8TwdBK3m9SNC
  These pages can be public: keep reports free of anything private (no email addresses, home addresses or account details).
- **Email:** Only if a Gmail tool is available in the session. Send the report to the `email_to` address in the agent's config file. If that address is blank or there's no Gmail tool, skip email silently. The report in the repo is the deliverable.
- **Network:** The shell may not be able to reach outside APIs. If a script fails on network access, follow the fallback in the relevant subagent file rather than retrying the same command.
