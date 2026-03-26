from __future__ import annotations

from aegisap.day6.state.models import Day6ReviewInput, InjectionSignal


OVERRIDE_PATTERNS = {
    "ignore prior rules": "UNTRUSTED_OVERRIDE_REQUEST",
    "approve urgently": "PROMPT_INJECTION_ATTEMPT",
    "skip review": "PROMPT_INJECTION_ATTEMPT",
    "bypass": "PROMPT_INJECTION_ATTEMPT",
    "do not escalate": "UNTRUSTED_OVERRIDE_REQUEST",
    "just process this now": "PROMPT_INJECTION_ATTEMPT",
    "confirmed by phone": "UNVERIFIED_APPROVAL_CLAIM",
}


def detect_prompt_injection(review_input: Day6ReviewInput) -> list[InjectionSignal]:
    signals: list[InjectionSignal] = []
    for evidence in review_input.evidence_ledger:
        lowered = evidence.extract.lower()
        for pattern in OVERRIDE_PATTERNS:
            if pattern in lowered:
                signals.append(
                    InjectionSignal(
                        evidence_id=evidence.evidence_id,
                        signal=pattern,
                        severity="high" if pattern != "confirmed by phone" else "medium",
                    )
                )
    for flag in review_input.injection_flags:
        signals.append(
            InjectionSignal(
                evidence_id="review_input",
                signal=flag,
                severity="high",
            )
        )
    unique: dict[tuple[str, str], InjectionSignal] = {}
    for signal in signals:
        unique[(signal.evidence_id, signal.signal)] = signal
    return list(unique.values())

