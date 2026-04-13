---
description: "Python backend and tests"
applyTo: "**/*.py,**/tests/**"
---

## Python Backend Instructions

- Use type hints consistently.
- Keep modules organized by feature or capability instead of building monoliths.
- Keep HTTP or CLI handlers thin; move business logic into services or domain modules.
- Prefer explicit request and response models for external boundaries.
- Use structured error handling rather than broad exception swallowing.
- Avoid logging secrets, credentials, or sensitive payloads.
- Make retries explicit and bounded; use exponential backoff for unstable network calls.
- Ensure async or queue consumers are idempotent when they can be retried.
- Add concise docstrings for public functions, classes, and modules when behavior is not obvious.
- Keep tests deterministic and focused on changed behavior.
- Prefer fixtures and builders over large inline payload blobs.
- Add edge-case and failure-path coverage when behavior changes.

### Example patterns

- router or handler delegates to a service
- service owns orchestration and validation
- adapters or clients isolate external-system details
