# Day 01 — Portal-First System Map

> **Portal mode:** `Inspect`  
> **Intent:** anchor the Day 1 business and system model in real Azure resources before the notebook abstracts them.

## Portal-First Outcome

You can map the live Azure substrate from Day 0 to the Day 1 explanation of what
an agentic system is, which services matter, and where identity boundaries live.

## Portal Mode

Do not hand-configure new Azure resources on Day 1. Inspect the surfaces that
already exist and connect them to the system story in your own words.

## Azure Portal Path

1. Open the Day 0 resource group and list every resource that already exists.
2. Open the Foundry resource and inspect the deployed model surface you will later call from the intake flow.
3. Open the AI Foundry playground and paste the invoice text from `fixtures/golden_thread/package.json` at `attachments[0].extracted_text`.
4. Ask the model to return JSON matching the Day 1 candidate shape: `supplier_name_text`, `invoice_number_text`, `invoice_date_text`, `currency_text`, `net_amount`, `vat_amount`, `gross_amount`, `po_reference_text`, and `bank_details_text`.
5. Save that raw JSON candidate exactly as returned so you can compare it to the notebook's deterministic validation and rejection logic.
6. Open Azure AI Search and identify the retrieval surface that becomes important on Day 3.
7. Open Key Vault or note its future role if you are still on the `core` track.
8. Open any Container Apps or monitoring resources that already exist and note which are runtime concerns rather than Day 1 requirements.
9. Open **Access control (IAM)** on one Azure resource and identify the least-privilege runtime role versus a broader developer role.

## What To Capture

- A resource inventory grouped into `reasoning`, `retrieval`, `runtime`, `secret`, and `observability` surfaces.
- The raw JSON candidate produced by the Foundry playground from the Day 1 invoice text.
- One example of a narrow runtime role and why it is safer than broader access.
- One sentence per resource answering: "Why does this exist in the AegisAP story?"

## Three-Surface Linkage

- `Portal`: inspect the Day 0 Azure substrate, then manually run the Day 1 invoice text through the AI Foundry playground and capture the raw candidate JSON.
- `Notebook`: open [day_1_agentic_fundamentals.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_1_agentic_fundamentals.py), use the Direct Day 1 Boundary Walkthrough, and paste the portal candidate into the notebook bridge so the same candidate is forced through canonicalization or rejection.
- `Automation`: run `uv run python scripts/run_day1_intake.py --mode fixture` only after the portal candidate and notebook boundary behavior make sense.
- `Evidence`: the Foundry candidate, the notebook's canonical invoice or rejection result, and `build/day1/golden_thread_day1.json` should all describe the same intake story.

## Handoff To Notebook

- Open [day_1_agentic_fundamentals.py](/workspaces/agentic-accounts-payable-orchestrator/notebooks/day_1_agentic_fundamentals.py).
- Use [DAY_01.md](/workspaces/agentic-accounts-payable-orchestrator/docs/DAY_01.md) to connect the portal inventory to business value and trust boundaries.

## Handoff To Automation

The Day 1 script is a reproducibility wrapper, not the first learning surface:

```bash
uv run python scripts/run_day1_intake.py --mode fixture
```

Run it only after you can explain how Foundry fits into the intake boundary and
why the system still needs deterministic validation.
