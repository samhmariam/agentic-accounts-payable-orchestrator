# Day 03 Bridge — Retrieval Authority

## Portal Signal

- Azure AI Search still contains both the stale email and the authoritative vendor record.
- The wrong source is winning because authority logic drifted.

## Notebook Proof

- Run the ranking preview and workflow preview.
- Prove the structured source must outrank the stale email without deleting history.

## Production Codification

- `src/aegisap/day3/policies/source_authority_rules.yaml`: codify source precedence.
- `src/aegisap/day3/retrieval/ranker.py`: codify the ranking math.
- `src/aegisap/day3/retrieval/authority_policy.py`: keep policy loading aligned.

## Export To Production

- Which portal document was wrongly winning?
- Which notebook score or field proved the correction?
- Which policy or ranker lines must change to make that order permanent?
