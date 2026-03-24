from __future__ import annotations

import json
from pathlib import Path

from ..state.evidence_models import EvidenceItem
from .interfaces import day3_data_path, parse_iso_date


class StructuredPOLookup:
    def __init__(
        self,
        po_path: str | Path | None = None,
        receipt_path: str | Path | None = None,
    ) -> None:
        self.po_path = Path(po_path or day3_data_path("structured", "purchase_orders.json"))
        self.receipt_path = Path(receipt_path or day3_data_path("structured", "goods_receipts.json"))

    def search(self, *, po_number: str | None) -> list[EvidenceItem]:
        if not po_number:
            return []

        po_rows = json.loads(self.po_path.read_text(encoding="utf-8"))
        receipt_rows = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        results: list[EvidenceItem] = []

        for row in po_rows:
            if row["po_number"] != po_number:
                continue
            results.append(
                EvidenceItem(
                    evidence_id=f'po-{row["po_number"]}',
                    source_name="purchase_orders",
                    source_type="po_table",
                    backend="structured_lookup",
                    authority_tier=1,
                    event_time=parse_iso_date(row.get("approval_date")),
                    ingest_time=parse_iso_date(row.get("ingest_date")),
                    retrieval_score=0.99,
                    citation=(
                        f'PO {row["po_number"]} approved for vendor {row["vendor_id"]} '
                        f'with total amount {row["amount"]} {row["currency"]}.'
                    ),
                    raw_ref=f'purchase_orders:{row["po_number"]}',
                    content=json.dumps(row, sort_keys=True),
                    metadata=row,
                )
            )

        for row in receipt_rows:
            if row["po_number"] != po_number:
                continue
            results.append(
                EvidenceItem(
                    evidence_id=f'gr-{row["po_number"]}',
                    source_name="goods_receipts",
                    source_type="goods_receipt",
                    backend="structured_lookup",
                    authority_tier=1,
                    event_time=parse_iso_date(row.get("receipt_date")),
                    ingest_time=parse_iso_date(row.get("ingest_date")),
                    retrieval_score=0.95,
                    citation=(
                        f'Goods receipt for PO {row["po_number"]} shows all_received='
                        f'{row["all_received"]} and received_total {row["received_total"]}.'
                    ),
                    raw_ref=f'goods_receipts:{row["po_number"]}',
                    content=json.dumps(row, sort_keys=True),
                    metadata=row,
                )
            )

        return results
