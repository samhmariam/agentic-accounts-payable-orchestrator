from __future__ import annotations

import asyncio

from aegisap.day4.planning.azure_openai_planner import AzureOpenAIPlannerClient
from aegisap.day_01.agent import extract_candidate
from aegisap.day_01.models import AttachmentInput, EvidenceValue, ExtractedInvoiceCandidate, InvoicePackageInput


def test_day1_extraction_uses_shared_model_gateway(monkeypatch) -> None:
    called: list[str] = []

    def fake_invoke(self, request):
        called.append(request.task_class)
        candidate = ExtractedInvoiceCandidate(
            supplier_name_text="Contoso Ltd",
            invoice_number_text="INV-1001",
            invoice_date_text="2026-03-01",
            currency_text="GBP",
            net_amount=EvidenceValue(pdf_text="100.00"),
            vat_amount=EvidenceValue(pdf_text="20.00"),
            gross_amount=EvidenceValue(pdf_text="120.00"),
            po_reference_text="PO-1001",
            bank_details_text="1234",
        )
        return candidate.model_dump_json(), None, None

    monkeypatch.setattr("aegisap.day_01.agent.ModelGateway.invoke_text", fake_invoke)

    package = InvoicePackageInput(
        message_id="msg-1",
        email_subject="Invoice",
        email_body="Please process",
        attachments=[
            AttachmentInput(
                filename="invoice.pdf",
                content_type="application/pdf",
                sha256="a" * 64,
                extracted_text="invoice attachment",
            )
        ],
    )
    candidate = extract_candidate(package)

    assert called == ["extract"]
    assert candidate.invoice_number_text == "INV-1001"


def test_day4_planner_uses_shared_model_gateway(monkeypatch) -> None:
    called: list[str] = []

    def fake_invoke(self, request):
        called.append(request.task_class)
        return '{"plan_id": "plan-1"}', type("Decision", (), {"deployment_name": "gpt-4.1", "reason": "plan_defaults_to_strong"})(), type("Entry", (), {"task_class": "plan"})()

    monkeypatch.setattr("aegisap.day4.planning.azure_openai_planner.ModelGateway.invoke_text", fake_invoke)

    result = asyncio.run(AzureOpenAIPlannerClient().invoke("Return JSON"))

    assert called == ["plan"]
    assert result == '{"plan_id": "plan-1"}'
