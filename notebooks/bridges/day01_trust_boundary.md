# Day 01 Bridge — Trust Boundary Intake

## Portal Signal

- Foundry or Azure OpenAI extraction is healthy.
- The raw candidate payload still contains the failing locale-formatted amount.

## Notebook Proof

- Run the amount preview and fixture walkthrough.
- Prove the deterministic normalizer or reject path is wrong.

## Production Codification

- `src/aegisap/day_01/normalizers.py`: make locale-safe amount parsing permanent.
- `src/aegisap/day_01/service.py`: keep rejection behavior aligned with the repaired parser.

## Export To Production

- Which exact amount literal crossed the trust boundary?
- Which exact normalization rule must change?
- Which test proves valid locale input now passes without weakening malformed-input rejection?
