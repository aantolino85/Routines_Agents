You are running the weekly Alternatives Deal Desk (RIA lens) in the Routines_Agents repo.
Run the /alts workflow: follow CLAUDE.md and alternatives/CLAUDE.md for the last 7 days. Launch one alts-scout per
bucket in alternatives/config/coverage.yaml in parallel (plus one for manager_watch), merge and deduplicate against
alternatives/data/deal_log.csv, write alternatives/digests/<today>.md, append the new transactions to the log, commit and push,
and email it if a Gmail tool is available and email_to is set in alternatives/config/coverage.yaml.
