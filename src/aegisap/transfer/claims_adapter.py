from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


HIGH_VALUE_THRESHOLD_USD = Decimal("2500.00")
KNOWN_DUPLICATE_CLAIMS: set[str] = set()
PROCEDURE_TO_DIAGNOSIS_PREFIXES = {
    "E0601": ("G47",),
    "E0162": ("M54",),
    "E0143": ("M", "R26"),
    "K0005": ("G80", "M62"),
    "E1399": ("G80", "M62"),
    "A4253": ("E11",),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ControlSignals(StrictModel):
    case_id: str
    source_domain: str = "claims_intake"
    claim_number: str
    billed_amount_usd: Decimal | None = None
    high_value_threshold_usd: Decimal = HIGH_VALUE_THRESHOLD_USD
    high_value: bool = False
    authorisation_present: bool = False
    duplicate_detected: bool = False
    code_mismatch: bool = False
    malformed_amount: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)
    manual_review_reasons: list[str] = Field(default_factory=list)
    procedure_codes: list[str] = Field(default_factory=list)
    diagnosis_codes: list[str] = Field(default_factory=list)
    raw_shape_notes: list[str] = Field(default_factory=list)


class ClaimsTransferDecision(StrictModel):
    outcome: str
    reason_codes: list[str] = Field(default_factory=list)
    manual_review_required: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)


def load_claim_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def adapt_claim_to_control_signals(
    payload: dict[str, Any],
    *,
    known_duplicates: set[str] | None = None,
    high_value_threshold_usd: Decimal = HIGH_VALUE_THRESHOLD_USD,
) -> ControlSignals:
    claim_number = _extract_claim_number(payload)
    diagnosis_codes = _extract_diagnosis_codes(payload)
    procedure_codes = _extract_procedure_codes(payload)
    authorisation_ref = _extract_authorisation_reference(payload)
    billed_amount = _extract_total_amount(payload)
    related_duplicate_reference = _extract_duplicate_reference(payload)
    duplicates = known_duplicates or KNOWN_DUPLICATE_CLAIMS

    blocking_reasons: list[str] = []
    manual_review_reasons: list[str] = []
    raw_shape_notes = [
        "FHIR-like identifier arrays are flattened before control evaluation.",
        "Procedure and diagnosis codings are normalized from nested CodeableConcept arrays.",
    ]
    if related_duplicate_reference:
        raw_shape_notes.append(
            "Duplicate detection considered the related-claim reference carried by the hostile payload."
        )

    malformed_amount = billed_amount is None
    if malformed_amount:
        blocking_reasons.append("MALFORMED_AMOUNT_FIELD")

    authorisation_present = bool(authorisation_ref)
    if not authorisation_present:
        blocking_reasons.append("MISSING_AUTH")

    duplicate_detected = claim_number in duplicates or related_duplicate_reference is not None
    if duplicate_detected:
        blocking_reasons.append("DUPLICATE_DETECTED")

    code_mismatch = _has_code_mismatch(procedure_codes=procedure_codes, diagnosis_codes=diagnosis_codes)
    if code_mismatch:
        blocking_reasons.append("CODE_MISMATCH")

    high_value = bool(billed_amount is not None and billed_amount > high_value_threshold_usd)
    if high_value:
        manual_review_reasons.append("HIGH_VALUE_CLAIM")

    return ControlSignals(
        case_id=str(payload.get("_case") or claim_number),
        claim_number=claim_number,
        billed_amount_usd=billed_amount,
        high_value_threshold_usd=high_value_threshold_usd,
        high_value=high_value,
        authorisation_present=authorisation_present,
        duplicate_detected=duplicate_detected,
        code_mismatch=code_mismatch,
        malformed_amount=malformed_amount,
        blocking_reasons=list(dict.fromkeys(blocking_reasons)),
        manual_review_reasons=list(dict.fromkeys(manual_review_reasons)),
        procedure_codes=procedure_codes,
        diagnosis_codes=diagnosis_codes,
        raw_shape_notes=raw_shape_notes,
    )


def evaluate_control_signals(signals: ControlSignals) -> ClaimsTransferDecision:
    if signals.blocking_reasons:
        return ClaimsTransferDecision(
            outcome="refused",
            reason_codes=list(signals.blocking_reasons),
            manual_review_required=False,
            blocking_reasons=list(signals.blocking_reasons),
        )
    if signals.manual_review_reasons:
        return ClaimsTransferDecision(
            outcome="pending_adjudicator_review",
            reason_codes=list(signals.manual_review_reasons),
            manual_review_required=True,
            blocking_reasons=[],
        )
    return ClaimsTransferDecision(
        outcome="auto_approved",
        reason_codes=[],
        manual_review_required=False,
        blocking_reasons=[],
    )


def _extract_claim_number(payload: dict[str, Any]) -> str:
    identifiers = payload.get("identifier") or []
    for identifier in identifiers:
        type_code = (
            ((identifier.get("type") or {}).get("coding") or [{}])[0].get("code")
            if isinstance(identifier, dict)
            else None
        )
        value = identifier.get("value") if isinstance(identifier, dict) else None
        if type_code == "claim-number" and value:
            return str(value)
    for identifier in identifiers:
        if isinstance(identifier, dict) and identifier.get("value"):
            return str(identifier["value"])
    raise ValueError("Claim payload is missing an identifier value.")


def _extract_procedure_codes(payload: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for item in payload.get("item") or []:
        codings = (((item.get("productOrService") or {}).get("coding")) or [])
        for coding in codings:
            code = str(coding.get("code", "")).strip()
            if code:
                codes.append(code)
    return list(dict.fromkeys(codes))


def _extract_diagnosis_codes(payload: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for diagnosis in payload.get("diagnosis") or []:
        codings = ((((diagnosis.get("diagnosisCodeableConcept") or {}).get("coding")) or []))
        for coding in codings:
            code = str(coding.get("code", "")).strip()
            if code:
                codes.append(code)
    return list(dict.fromkeys(codes))


def _extract_authorisation_reference(payload: dict[str, Any]) -> str | None:
    for entry in payload.get("supportingInfo") or []:
        category_codes = [
            str(coding.get("code", "")).strip()
            for coding in (((entry.get("category") or {}).get("coding")) or [])
        ]
        if "priorauth" not in category_codes:
            continue
        value = (((entry.get("valueReference") or {}).get("identifier")) or {}).get("value")
        if value:
            return str(value)
    return None


def _extract_total_amount(payload: dict[str, Any]) -> Decimal | None:
    total = payload.get("total") or {}
    raw_value = total.get("value")
    if raw_value is None:
        return None
    if isinstance(raw_value, (int, float)):
        return Decimal(str(raw_value))
    text = str(raw_value).strip()
    if not text or "," in text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _extract_duplicate_reference(payload: dict[str, Any]) -> str | None:
    for relation in payload.get("related") or []:
        relationship_codes = [
            str(coding.get("code", "")).strip().lower()
            for coding in (((relation.get("relationship") or {}).get("coding")) or [])
        ]
        if "duplicate" not in relationship_codes:
            continue
        claim_identifier = (((relation.get("claim") or {}).get("identifier")) or {}).get("value")
        if claim_identifier:
            return str(claim_identifier)
    return None


def _has_code_mismatch(*, procedure_codes: list[str], diagnosis_codes: list[str]) -> bool:
    if not procedure_codes or not diagnosis_codes:
        return False
    for procedure_code in procedure_codes:
        allowed_prefixes = PROCEDURE_TO_DIAGNOSIS_PREFIXES.get(procedure_code, ())
        if not allowed_prefixes:
            continue
        if not any(diagnosis_code.startswith(prefix) for prefix in allowed_prefixes for diagnosis_code in diagnosis_codes):
            return True
    return False
