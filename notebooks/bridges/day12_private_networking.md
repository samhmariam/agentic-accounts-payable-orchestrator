# Day 12 Bridge — Private Networking

## Portal Signal

- Networking surfaces show public access, DNS drift, or broken private endpoint wiring.
- Static artifacts and live posture no longer tell the same story.

## Notebook Proof

- Use the static policy checker preview to prove the failing property path.
- Compare that result with live DNS or reachability evidence.

## Production Codification

- `src/aegisap/network/bicep_policy_checker.py`: codify the correct static property inspection.
- `src/aegisap/network/private_endpoint_probe.py`: codify live posture checks.
- `scripts/check_private_network_static.py` and `scripts/verify_private_network_posture.py`: keep the artifact contract aligned.

## Export To Production

- Which portal or Network Watcher signal proved the drift?
- Which notebook output proved the checker bug?
- Which code path makes the private-only rule durable?
