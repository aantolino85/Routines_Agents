# Routines_Agents

Two Claude Code agents, each with its own schedule:

- **Personal concierge** (`/weekend`, Thursday evening): ranks your ski mountains (Wachusett, Waterville Valley,
  Loon, Killington, Stowe), picks the top 5 nights out near Andover, and finds dog events and boarding deals.
- **Professional deal desk** (`/deals`, Monday morning): a digest of energy and data center transactions, market
  shifts and policy or legal changes, plus an "angle for Angelo" section. Every deal is also logged to a CSV.

## Layout
```
CLAUDE.md                 routing + house rules (read automatically)
.claude/agents/           subagents: powder-scout, nightlife-scout, dog-scout, deal-scout
.claude/commands/         /weekend, /deals
personal/                 CLAUDE.md, config/*.yaml, scripts/snow_report.py, reports/
professional/             CLAUDE.md, config/coverage.yaml, digests/, data/deal_log.csv
prompts/                  text for the two scheduled tasks
```

## Customize (all plain YAML)
- `personal/config/mountains.yaml`: add or remove mountains, drive times, scoring thresholds
- `personal/config/nightlife.yaml`: favorite artists, regular venues, genres to skip
- `personal/config/dog.yaml`: dog's name, size and temperament
- `professional/config/coverage.yaml`: deal size thresholds, buckets, search terms, sources
- `email_to` in `personal/config/home.yaml` and `professional/config/coverage.yaml`: turns on email delivery

## Run manually
Open a Claude Code session on this repo and type `/weekend` or `/deals`. You can add extra instructions,
e.g. `/weekend I'm off Friday` or `/deals focus on ERCOT this week`.

## Snow script
`python3 personal/scripts/snow_report.py` pulls Open-Meteo forecasts (free, no key). If the environment blocks
`api.open-meteo.com`, the powder-scout subagent falls back automatically. For the fastest and most reliable
numbers, allow that domain in your cloud environment's network settings.

## Ideas to grow it
- Score past forecasts against what actually fell, and tune the weights
- Add a `music-history` log so nightlife picks learn what you actually went to
- Have the deal desk build a running sponsor and lender league table from `deal_log.csv`
