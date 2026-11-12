You are running Angelo's weekly Energy & Data Center Deal Desk in the Routines_Agents repo.
Run the /deals workflow: follow CLAUDE.md and professional/CLAUDE.md for the last 7 days. Launch one deal-scout per
bucket in professional/config/coverage.yaml in parallel, merge and deduplicate against professional/data/deal_log.csv,
write professional/digests/<today>.md, append the new transactions to the log, commit and push, and email it if
a Gmail tool is available and email_to is set in professional/config/coverage.yaml.
