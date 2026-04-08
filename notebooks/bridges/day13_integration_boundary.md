# Day 13 Bridge — Integration Boundary

## Portal Signal

- The hosted integration revision is publishing a stale or incomplete capabilities contract.
- Partner-visible behavior and reliability evidence disagree.

## Notebook Proof

- Use the MCP capability preview to inspect the intended contract.
- Prove the governed write path must be advertised explicitly.

## Production Codification

- `src/aegisap/mcp/server.py`: codify the served contract.
- `src/aegisap/mcp/schemas.py`: codify the shape of the advertised capability.
- `src/aegisap/integration/dlq_consumer.py` or `src/aegisap/integration/compensating_action.py`: codify supporting reliability behavior when needed.

## Export To Production

- Which capability was missing for partners?
- Which notebook contract proved the correct boundary?
- Which production file publishes the durable fix?
