---
description: "Infrastructure as code and config"
applyTo: "**/infra/**,**/*.tf,**/*.yaml,**/*.yml"
---

## Infra Instructions

- Tag resources with service, environment, and ownership metadata when the platform supports it.
- Prefer least privilege over wildcard permissions.
- Add retention, lifecycle, or cleanup policies for storage resources.
- Add alerts or observable signals for failure, latency, or throttling risks.
- Include rollback awareness when changing production-facing infrastructure.
- Prefer explicit concurrency and cost guards for scheduled or batch workloads.
- Document any secret or parameter dependencies outside the repo.
- Keep environment-specific values out of committed defaults when possible.
- Treat public ingress, IAM, networking, and data-retention changes as higher risk.

### Review focus

- permissions scope
- data retention
- cost controls
- observability coverage
- safe rollout and rollback path
