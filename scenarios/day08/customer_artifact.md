# Customer Escalation: Runtime Search Access Drift

Subject: Runtime identity is over-privileged in staging

Platform Engineering found that the runtime identity can mutate the search index.
That is not an operator convenience issue. It is a production boundary failure.

You need to restore the Day 8 deployment contract:

1. Runtime access must return to reader-only scope.
2. Admin identities must keep the contributor privileges they actually need.
3. The release packet must explain the blast radius of over-privileged search access.

- Principal Cloud Architect
