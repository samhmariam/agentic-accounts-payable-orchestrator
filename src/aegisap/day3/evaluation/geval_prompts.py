FAITHFULNESS_PROMPT = """
You are grading whether a workflow answer is faithful to the cited evidence.

Score 1:
- unsupported claim appears
- answer ignores conflicting evidence
- citations are present but do not support the answer

Score 3:
- answer is mostly grounded
- one minor unsupported jump exists
- citations are partially aligned

Score 5:
- every material claim is supported by cited evidence
- conflicts are surfaced explicitly
- the answer does not smuggle in uncited facts
""".strip()

COMPLETENESS_PROMPT = """
You are grading whether the workflow answer covered the required decision surfaces.

Score 1:
- only one control surface is discussed
- major checks are missing

Score 3:
- most required checks are present
- one material check is thin or omitted

Score 5:
- vendor, PO, and policy implications are all covered where relevant
- the answer names the next operational step
""".strip()

POLICY_GROUNDING_PROMPT = """
You are grading whether the answer follows source-of-truth and authority-tier rules.

Score 1:
- low-authority evidence overrides a system of record
- stale evidence is treated as current truth

Score 3:
- policy intent is mostly followed
- one source-priority rule is ambiguous

Score 5:
- structured system-of-record data wins when facts conflict
- recency and authority are both visible in the reasoning
""".strip()
