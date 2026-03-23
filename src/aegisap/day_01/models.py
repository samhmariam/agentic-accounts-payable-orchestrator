from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveMoney = Annotated[
    Decimal,
    Field(gt=Decimal("0"), max_digits=18, decimal_places=2),
]

NonNegativeMoney = Annotated[
    Decimal,
    Field(ge=Decimal("0"), max_digits=18, decimal_places=2),
]


class AttachmentInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    filename: str
    content_type: str
    sha256: str
    extracted_text: str


class InvoicePackageInput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    message_id: str
    email_subject: str
    email_body: str
    attachments: list[AttachmentInput]


class EvidenceValue(BaseModel):
    """
    Raw text copied from the sources.
    Do not normalize separators here.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    pdf_text: str | None = None
    email_text: str | None = None

    @model_validator(mode="after")
    def require_one_source(self) -> "EvidenceValue":
        if not self.pdf_text and not self.email_text:
            raise ValueError("at least one evidence source is required")
        return self


class ExtractedInvoiceCandidate(BaseModel):
    """
    Agent output.
    This stays string-heavy on purpose so that deterministic Python owns
    parsing, normalization, and reconciliation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    supplier_name_text: str | None = None
    invoice_number_text: str | None = None
    invoice_date_text: str | None = None
    currency_text: str | None = None

    net_amount: EvidenceValue | None = None
    vat_amount: EvidenceValue | None = None
    gross_amount: EvidenceValue | None = None

    po_reference_text: str | None = None
    bank_details_text: str | None = None


class CanonicalInvoice(BaseModel):
    """
    The only object allowed to cross the Day 1 intake boundary.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    supplier_name: Annotated[str, Field(min_length=1, max_length=200)]
    invoice_number: Annotated[str, Field(min_length=1, max_length=100)]
    invoice_date: date
    currency: Annotated[str, Field(pattern=r"^[A-Z]{3}$")]

    net_amount: PositiveMoney
    vat_amount: NonNegativeMoney
    gross_amount: PositiveMoney

    po_reference: Annotated[str, Field(min_length=1, max_length=100)]
    bank_details_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]

    @model_validator(mode="after")
    def check_amount_identity(self) -> "CanonicalInvoice":
        total = (self.net_amount + self.vat_amount).quantize(Decimal("0.01"))
        if total != self.gross_amount:
            raise ValueError("net_amount + vat_amount must equal gross_amount")
        return self
