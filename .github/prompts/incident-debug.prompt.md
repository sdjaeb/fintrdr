# Incident Debug Prompt

For incident triage, collect:

- the exact failing signal
- recent deploys or config changes
- logs, metrics, and traces for the affected flow
- queue depth, retries, throttling, and error-rate signals

First steps:

1. isolate the failing boundary
2. assess blast radius and rollback options
3. stop guessing and gather the next missing piece of evidence
4. record the recovery signal that will prove the system is healthy again
