# Day 07 Bridge — Guardrail Redaction

## Portal Signal

- Application Insights or Log Analytics shows raw identifiers leaking in a refusal event.
- The live payload violates the governance packet.

## Notebook Proof

- Use the redaction preview and audit-event preview.
- Prove the repair removes sensitive data while preserving operator-usable context.

## Production Codification

- `src/aegisap/security/redaction.py`: codify the masking rules.
- `src/aegisap/audit/events.py`: codify safe audit shaping.
- `src/aegisap/audit/writer.py`: only change if persistence is writing the wrong payload.

## Export To Production

- Which field or token leaked?
- Which notebook output proved the corrected redaction?
- Which repo file permanently removes the leak before persistence?
