from __future__ import annotations

from pathlib import Path

from aegisap.audit.events import build_audit_event, buffer_audit_event
from aegisap.common.paths import repo_root
from aegisap.day3.agents.po_match_agent import verify_po_match
from aegisap.day3.agents.vendor_risk_verifier import verify_vendor_risk
from aegisap.day3.retrieval.structured_po_lookup import StructuredPOLookup
from aegisap.day3.retrieval.structured_vendor_lookup import StructuredVendorLookup
from aegisap.day4.execution.task_contracts import WorkerExecutor, WorkerTaskInput
from aegisap.day4.planning.plan_types import EvidenceRef, TaskResult
from aegisap.observability.retry_policy import RetryPolicy, execute_with_retry
from aegisap.observability.tracing import add_span_event, node_span_attributes, start_observability_span

READ_RETRY_POLICY = RetryPolicy(max_attempts=3, initial_backoff_ms=100, max_backoff_ms=400, deadline_ms=2_000)


def _to_evidence_refs(evidence_ids: list[str]) -> list[EvidenceRef]:
    refs: list[EvidenceRef] = []
    for evidence_id in evidence_ids:
        if evidence_id.startswith(("po-", "gr-", "vendor-master-", "supplier_master:")):
            source_type = "structured"
        elif evidence_id.startswith("policy:"):
            source_type = "policy"
        elif evidence_id.startswith("email:"):
            source_type = "email"
        else:
            source_type = "document"
        refs.append(EvidenceRef(source_id=evidence_id, source_type=source_type))
    return refs


def _buffer_sensitive_event(
    *,
    state,
    action_type: str,
    decision_outcome: str,
    summary: str,
    evidence_refs: list[str],
    metadata: dict[str, object] | None = None,
) -> None:
    event = build_audit_event(
        workflow_run_id=state.workflow_run_id,
        thread_id=f"case:{state.case_facts.case_id}",
        state_version=0,
        actor_type="system_job",
        actor_id=f"day4:{action_type}",
        action_type=action_type,
        decision_outcome=decision_outcome,
        evidence_summary=summary,
        evidence_refs=evidence_refs,
        planner_version=state.planning.plan_version or "day4",
        metadata=metadata or {},
    )
    buffer_audit_event(state.artifacts, event)


class PolicyRetrievalWorker:
    task_type = "policy_retrieval"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        with start_observability_span(
            "dep.external_policy_doc_fetch",
            attributes=node_span_attributes(node_name="external_policy_doc_fetch", idempotent=True),
        ):
            policy_path = repo_root(__file__) / "data" / "day3" / "unstructured" / "ap_policy_bank_change.md"
            citation_ref = f"file:{policy_path.relative_to(repo_root(__file__))}"
            policy_requirements = [
                "Recommendations must remain blocked until mandatory controls are satisfied.",
            ]

            if not state.case_facts.po_present:
                policy_requirements.append("Missing PO cases require PO verification or an approved waiver.")
            if state.case_facts.bank_details_changed:
                policy_requirements.append("Changed bank details require authoritative verification.")
            if state.case_facts.invoice_amount_gbp >= (
                state.case_facts.amount_approval_threshold_gbp or 25_000
            ):
                policy_requirements.append("High-value invoices require an approval route before recommendation.")

        return TaskResult(
            task_id=input_data.task_id,
            status="completed",
            confidence=0.99,
            outputs={
                "policy_requirements": policy_requirements,
                "citation_refs": [citation_ref],
                "confidence": 0.99,
            },
            evidence_refs=[EvidenceRef(source_id=citation_ref, source_type="policy")],
        )


class POMatchVerificationWorker:
    task_type = "po_match_verification"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        invoice = {
            "vendor_id": state.case_facts.supplier_id,
            "po_number": state.case_facts.po_number,
            "amount": state.case_facts.invoice_amount_gbp,
        }
        with start_observability_span(
            "dep.structured_po_lookup.read",
            attributes=node_span_attributes(node_name="structured_po_lookup", idempotent=True),
        ):
            evidence = execute_with_retry(
                StructuredPOLookup().search,
                policy=READ_RETRY_POLICY,
                node_name=self.task_type,
                dependency_name="structured_po_lookup",
                idempotent=True,
                decision_reason_code="PO_LOOKUP",
                kwargs={"po_number": state.case_facts.po_number},
            )
        finding = verify_po_match(invoice, evidence)

        matched_fields: list[str] = []
        missing_fields: list[str] = []
        mismatch_flags: list[str] = []
        status = "completed"
        blocking_reason = None

        if finding.status == "pass":
            matched_fields = ["po_number", "vendor_id", "amount"]
        else:
            status = "blocked"
            if finding.status == "missing_po":
                missing_fields.append("po_number")
                blocking_reason = "missing_required_po_evidence"
            else:
                mismatch_flags.append(finding.recommended_action)
                blocking_reason = "po_condition_unsatisfied"

        _buffer_sensitive_event(
            state=state,
            action_type="po_match_check",
            decision_outcome="completed" if status == "completed" else "needs_human_review",
            summary=f"PO match verification returned {finding.status} for invoice {state.case_facts.invoice_id}.",
            evidence_refs=finding.evidence_ids,
            metadata={"status": finding.status, "confidence": finding.confidence},
        )
        return TaskResult(
            task_id=input_data.task_id,
            status=status,
            confidence=finding.confidence,
            outputs={
                "po_match_status": finding.status,
                "matched_fields": matched_fields,
                "missing_fields": missing_fields,
                "mismatch_flags": mismatch_flags,
                "confidence": finding.confidence,
            },
            blocking_reason=blocking_reason,
            evidence_refs=_to_evidence_refs(finding.evidence_ids),
        )


class POWaiverCheckWorker:
    task_type = "po_waiver_check"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        waiver_ref = next(
            (evidence_id for evidence_id in state.retrieved_evidence if evidence_id.startswith("waiver:")),
            None,
        )

        if state.case_facts.po_present:
            return TaskResult(
                task_id=input_data.task_id,
                status="completed",
                confidence=1.0,
                outputs={
                    "waiver_present": False,
                    "waiver_authority": "not_required",
                    "confidence": 1.0,
                },
            )

        if waiver_ref:
            return TaskResult(
                task_id=input_data.task_id,
                status="completed",
                confidence=0.95,
                outputs={
                    "waiver_present": True,
                    "waiver_authority": waiver_ref.split(":", 1)[1] or "approved_waiver",
                    "confidence": 0.95,
                },
                evidence_refs=[EvidenceRef(source_id=waiver_ref, source_type="document")],
            )

        return TaskResult(
            task_id=input_data.task_id,
            status="blocked",
            confidence=0.98,
            outputs={
                "waiver_present": False,
                "waiver_authority": "missing",
                "confidence": 0.98,
            },
            blocking_reason="missing_required_po_evidence",
        )


class VendorHistoryCheckWorker:
    task_type = "vendor_history_check"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        with start_observability_span(
            "dep.structured_vendor_lookup.read",
            attributes=node_span_attributes(node_name="structured_vendor_lookup", idempotent=True),
        ):
            evidence = execute_with_retry(
                StructuredVendorLookup().search,
                policy=READ_RETRY_POLICY,
                node_name=self.task_type,
                dependency_name="structured_vendor_lookup",
                idempotent=True,
                decision_reason_code="VENDOR_HISTORY_LOOKUP",
                kwargs={
                    "vendor_id": state.case_facts.supplier_id,
                    "vendor_name": state.case_facts.supplier_name,
                },
            )
        finding = verify_vendor_risk(
            {
                "vendor_id": state.case_facts.supplier_id,
                "vendor_name": state.case_facts.supplier_name,
            },
            evidence,
        )

        if evidence:
            outputs = {
                "supplier_history_summary": finding.key_findings,
                "risk_level": finding.risk_level,
                "confidence": finding.confidence,
            }
            result_status = "completed"
            blocking_reason = None
            evidence_refs = _to_evidence_refs(finding.evidence_ids)
            confidence = finding.confidence
        elif state.case_facts.supplier_exists:
            outputs = {
                "supplier_history_summary": [
                    "Normalized case facts indicate the supplier is an existing supplier.",
                    "Structured vendor history was not required to keep the recommendation path open.",
                ],
                "risk_level": "low",
                "confidence": 0.9,
            }
            result_status = "completed"
            blocking_reason = None
            evidence_refs = _to_evidence_refs(
                [evidence_id for evidence_id in state.retrieved_evidence if evidence_id.startswith("supplier_master:")]
            )
            confidence = 0.9
        else:
            outputs = {
                "supplier_history_summary": ["No supplier history was available for the case."],
                "risk_level": "high",
                "confidence": 0.35,
            }
            result_status = "blocked"
            blocking_reason = "missing_supplier_history"
            evidence_refs = []
            confidence = 0.35

        _buffer_sensitive_event(
            state=state,
            action_type="vendor_check",
            decision_outcome="completed" if result_status == "completed" else "needs_human_review",
            summary=(
                f"Vendor history check completed with risk level {outputs['risk_level']} "
                f"for supplier {state.case_facts.supplier_id}."
            ),
            evidence_refs=[item.evidence_id for item in evidence] if evidence else [],
            metadata={"risk_level": outputs["risk_level"], "confidence": confidence},
        )
        return TaskResult(
            task_id=input_data.task_id,
            status=result_status,
            confidence=confidence,
            outputs=outputs,
            blocking_reason=blocking_reason,
            evidence_refs=evidence_refs,
        )


class VendorBankVerificationWorker:
    task_type = "vendor_bank_verification"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        with start_observability_span(
            "dep.structured_vendor_lookup.read",
            attributes=node_span_attributes(node_name="structured_vendor_lookup", idempotent=True),
        ):
            evidence = execute_with_retry(
                StructuredVendorLookup().search,
                policy=READ_RETRY_POLICY,
                node_name=self.task_type,
                dependency_name="structured_vendor_lookup",
                idempotent=True,
                decision_reason_code="BANK_VERIFICATION_LOOKUP",
                kwargs={
                    "vendor_id": state.case_facts.supplier_id,
                    "vendor_name": state.case_facts.supplier_name,
                },
            )
        evidence_ids = [item.evidence_id for item in evidence]

        bank_change_verified = bool(
            state.case_facts.bank_change_verified
            or any(evidence_id.startswith("approved_bank_change:") for evidence_id in state.retrieved_evidence)
        )

        if not state.case_facts.bank_details_changed:
            return TaskResult(
                task_id=input_data.task_id,
                status="completed",
                confidence=1.0,
                outputs={
                    "bank_change_verified": True,
                    "authoritative_source_checked": True,
                    "risk_level": "low",
                    "confidence": 1.0,
                },
                evidence_refs=_to_evidence_refs(evidence_ids),
            )

        if bank_change_verified:
            add_span_event(
                "cache_hit",
                {
                    "error_class": "none",
                    "attempt_number": 1,
                    "backoff_ms": 0,
                    "remaining_budget_ms": READ_RETRY_POLICY.deadline_ms,
                    "dependency_name": "structured_vendor_lookup",
                    "decision_reason_code": "BANK_CHANGE_VERIFIED",
                },
            )
            _buffer_sensitive_event(
                state=state,
                action_type="bank_detail_evaluation",
                decision_outcome="completed",
                summary=(
                    f"Bank detail verification passed for supplier {state.case_facts.supplier_id}."
                ),
                evidence_refs=evidence_ids,
                metadata={"bank_change_verified": True},
            )
            return TaskResult(
                task_id=input_data.task_id,
                status="completed",
                confidence=0.98,
                outputs={
                    "bank_change_verified": True,
                    "authoritative_source_checked": True,
                    "risk_level": "low",
                    "confidence": 0.98,
                },
                evidence_refs=_to_evidence_refs(evidence_ids),
            )

        _buffer_sensitive_event(
            state=state,
            action_type="bank_detail_evaluation",
            decision_outcome="needs_human_review",
            summary=(
                f"Bank detail verification failed for supplier {state.case_facts.supplier_id}; "
                "manual review required."
            ),
            evidence_refs=evidence_ids,
            metadata={"bank_change_verified": False},
        )
        return TaskResult(
            task_id=input_data.task_id,
            status="escalated",
            confidence=0.99,
            outputs={
                "bank_change_verified": False,
                "authoritative_source_checked": bool(evidence),
                "risk_level": "high",
                "confidence": 0.99,
            },
            blocking_reason="unverified_bank_change",
            evidence_refs=_to_evidence_refs(evidence_ids),
        )


class ThresholdApprovalCheckWorker:
    task_type = "threshold_approval_check"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        amount_threshold = state.case_facts.amount_approval_threshold_gbp or 25_000
        controller_threshold = state.case_facts.controller_approval_threshold_gbp or 40_000

        required_approvals: list[str] = []
        if state.case_facts.invoice_amount_gbp >= amount_threshold:
            required_approvals.append("ap_manager")
        if state.case_facts.invoice_amount_gbp >= controller_threshold:
            required_approvals.append("controller")

        _buffer_sensitive_event(
            state=state,
            action_type="high_value_escalation",
            decision_outcome="completed" if required_approvals else "completed",
            summary=(
                f"Threshold approval check identified approvals {required_approvals or ['none']} "
                f"for invoice amount {state.case_facts.invoice_amount_gbp}."
            ),
            evidence_refs=["policy:approval-thresholds"],
            metadata={"required_approvals": required_approvals},
        )
        return TaskResult(
            task_id=input_data.task_id,
            status="completed",
            confidence=0.97,
            outputs={
                "required_approvals": required_approvals,
                "approval_path_defined": bool(required_approvals),
                "confidence": 0.97,
            },
        )


class ManualEscalationPackageWorker:
    task_type = "manual_escalation_package"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        add_span_event(
            "human_review_escalated",
            {
                "error_class": "manual_escalation_package",
                "attempt_number": 1,
                "backoff_ms": 0,
                "remaining_budget_ms": 0,
                "dependency_name": self.task_type,
                "decision_reason_code": "MANUAL_ESCALATION_PACKAGE",
            },
        )
        reasons = list(
            dict.fromkeys(
                state.eligibility.blocking_conditions
                + state.eligibility.unmet_preconditions
                + state.plan.global_stop_conditions
            )
        )

        return TaskResult(
            task_id=input_data.task_id,
            status="completed",
            confidence=1.0,
            outputs={
                "escalation_reasons": reasons,
                "evidence_bundle": list(state.retrieved_evidence),
                "confidence": 1.0,
            },
            evidence_refs=_to_evidence_refs(list(state.retrieved_evidence)),
        )


class PaymentRecommendationDraftWorker:
    task_type = "payment_recommendation_draft"

    async def execute(self, input_data: WorkerTaskInput) -> TaskResult:
        state = input_data.workflow_state
        return TaskResult(
            task_id=input_data.task_id,
            status="completed",
            confidence=0.94,
            outputs={
                "recommendation_draft": {
                    "case_id": state.case_facts.case_id,
                    "supplier_id": state.case_facts.supplier_id,
                    "invoice_id": state.case_facts.invoice_id,
                    "summary": "Draft recommendation assembled pending explicit gate approval.",
                },
                "confidence": 0.94,
            },
        )


def default_workers() -> list[WorkerExecutor]:
    return [
        PolicyRetrievalWorker(),
        POMatchVerificationWorker(),
        POWaiverCheckWorker(),
        VendorHistoryCheckWorker(),
        VendorBankVerificationWorker(),
        ThresholdApprovalCheckWorker(),
        ManualEscalationPackageWorker(),
        PaymentRecommendationDraftWorker(),
    ]
