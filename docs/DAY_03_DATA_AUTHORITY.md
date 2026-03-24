# Day 3 - Data Authority

Day 3 introduces explicit source ranking so semantic relevance does not masquerade as truth.

## Authority tiers

- Tier 1: system of record such as vendor master, PO tables, and goods receipts
- Tier 2: approved workflow artifacts and policy documents
- Tier 3: business communications such as onboarding emails
- Tier 4: derived notes and model-generated summaries

## Ranking rule

Day 3 uses a composite score:

`final_score = retrieval_score * source_weight * recency_weight + exact_match_bonus`

This makes authority and recency visible in code instead of relying on prompt wording alone.

The same rule applies whether the unstructured evidence came from local fixtures or from the live Azure AI Search-backed path. Search ranking is treated only as retrieval relevance; it does not replace the authority logic.

## Conflict handling

When sources disagree:

1. Higher authority wins.
2. If authority ties, the newer effective date wins.
3. If both still tie, the workflow should escalate rather than invent certainty.

Lower-authority conflicting evidence is still retained as historical context when it helps explain why a decision was made.

## Live retrieval boundary

Day 3 now has a live Azure Search path, but authority control still belongs to the workflow code, not the Search service.

That means:

- Azure Search is responsible for finding candidate documents
- Day 3 ranking code is responsible for applying source authority and recency
- specialist agents are responsible for citing and interpreting ranked evidence

This boundary matters because enterprise retrieval relevance is not the same thing as enterprise truth.

## Exit-check scenario

The adversarial Day 3 case is:

- an old onboarding email contains bank account `1138`
- the current vendor master contains bank account `4421`
- retrieval returns both

The correct behavior is:

- keep both pieces of evidence
- rank the current vendor master above the old email
- cite the authoritative record in the final decision
- treat the email as stale historical context rather than current truth

That case should behave the same way in both `fixture` mode and `azure_search_live` mode.
