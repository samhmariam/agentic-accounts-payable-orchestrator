# Day 9 Cost Ledger and Evaluation Slices

Every live model invocation appends one ledger entry with:

- `task_class`
- `node_name`
- `deployment_name`
- prompt, completion, and total tokens
- `cached_hit`
- `latency_ms`
- `retry_count`
- `estimated_cost`
- `input_hash`
- `policy_version`
- `workflow_run_id`

## Required Slices

- clean routine invoices
- missing PO
- new vendor
- bank details changed
- contradictory VAT evidence
- cross-border or multi-currency
- retrieval ambiguity
- human-review-required

Routing or prompt changes do not ship unless the critical slices stay neutral or
improve.
