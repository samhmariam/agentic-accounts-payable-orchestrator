# Customer Escalation: Break-Glass Recovery Blocked

Subject: Break-glass deployment recovery is blocked and staging still looks over-privileged

Platform Engineering cannot clear the deployment drift because the break-glass
state path is blocked, and the runtime identity can still mutate the search
index. That is not an operator convenience issue. It is a production boundary
failure.

You need to restore the Day 8 deployment contract:

1. Break-glass recovery must work with raw Azure tooling when the helper path is unavailable.
2. Runtime access must return to reader-only scope.
3. Admin identities must keep the contributor privileges they actually need.
4. The release packet must explain the blast radius of over-privileged search access.

- Principal Cloud Architect
