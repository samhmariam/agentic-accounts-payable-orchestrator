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


def test_day1_extraction_accepts_legacy_live_payload_shape(monkeypatch) -> None:
    def fake_invoke(self, request):
        return (
            """{
                "invoice_number": "INV-3001",
                "invoice_date": "01/03/2026",
                "supplier_name": "Acme Office Supplies",
                "currency": "GBP",
                "net_amount": "10000.00 GBP",
                "vat_amount": "2500.00 GBP",
                "gross_amount": "12500.00 GBP",
                "po_reference": "PO-9001",
                "bank_details": "IBAN GB29NWBK60161331924421",
                "email_message_id": "msg-golden-001"
            }""",
            None,
            None,
        )

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

    assert candidate.invoice_number_text == "INV-3001"
    assert candidate.invoice_date_text == "01/03/2026"
    assert candidate.supplier_name_text == "Acme Office Supplies"
    assert candidate.currency_text == "GBP"
    assert candidate.net_amount is not None
    assert candidate.net_amount.pdf_text == "10000.00 GBP"
    assert candidate.po_reference_text == "PO-9001"
