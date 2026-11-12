# Routines_Agents

Angelo's two Claude Code agents. They live in one repo but are configured separately.

| Agent | Folder | Command | Schedule | Output |
|---|---|---|---|---|
| **Personal concierge** | `personal/` | `/weekend` | Wednesday 6:00pm ET | `personal/reports/YYYY-MM-DD.md` |
| **Professional deal desk** | `professional/` | `/deals` | Monday 7:40am ET | `professional/digests/YYYY-MM-DD.md` + `professional/data/deal_log.csv` |

## Routing
- For skiing, snow, nightlife, live music, trivia, dog events or the weekend, read `personal/CLAUDE.md` and follow it.
- For deals, energy, data centers, markets or policy, read `professional/CLAUDE.md` and follow it.
- Never mix the two. Personal reports contain no work content, and deal digests contain no personal content.

## Subagents (`.claude/agents/`)
- `powder-scout`: snow forecasts and mountain ranking (personal)
- `nightlife-scout`: live music, trivia and other nights out near Andover (personal)
- `dog-scout`: dog meetups, events and boarding or daycare deals near Andover (personal)
- `deal-scout`: searches one coverage bucket of energy and data center news (professional; run several in parallel)

## House rules
- **Dates:** Always work out "this week" and "this weekend" from today's actual date (America/New_York).
- **Sources:** Every event, deal or claim needs a source link. Never invent events, venues, prices or deal terms. If something can't be verified, leave it out.
- **Committing:** After writing a report, commit it with a message like `personal: weekend report 2026-11-13` or `deals: digest 2026-11-16` and push to the current branch.
- **Email:** Only if a Gmail tool is available in the session. Send the report to the `email_to` address in the agent's config file. If that address is blank or there's no Gmail tool, skip email silently. The report in the repo is the deliverable.
- **Network:** The shell may not be able to reach outside APIs. If a script fails on network access, follow the fallback in the relevant subagent file rather than retrying the same command.
