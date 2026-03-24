from __future__ import annotations

import json
from pathlib import Path

from ..state.evidence_models import EvidenceItem
from .interfaces import day3_data_path, parse_iso_date


class StructuredVendorLookup:
    def __init__(self, data_path: str | Path | None = None) -> None:
        self.data_path = Path(data_path or day3_data_path("structured", "vendor_master.json"))

    def search(self, *, vendor_id: str | None, vendor_name: str | None) -> list[EvidenceItem]:
        rows = json.loads(self.data_path.read_text(encoding="utf-8"))
        results: list[EvidenceItem] = []
        for row in rows:
            id_match = vendor_id and row["vendor_id"] == vendor_id
            name_match = vendor_name and row["vendor_name"].lower() == vendor_name.lower()
            if not (id_match or name_match):
                continue
            results.append(
                EvidenceItem(
                    evidence_id=f'vendor-master-{row["vendor_id"]}',
                    source_name="vendor_master",
                    source_type="erp_vendor_master",
                    backend="structured_lookup",
                    authority_tier=1,
                    event_time=parse_iso_date(row.get("last_approved_update")),
                    ingest_time=parse_iso_date(row.get("ingest_date")),
                    retrieval_score=0.99,
                    citation=(
                        f'Vendor master lists {row["vendor_name"]} with approved bank '
                        f'account ending {row["bank_account_last4"]}.'
                    ),
                    raw_ref=f'vendor_master:{row["vendor_id"]}',
                    content=json.dumps(row, sort_keys=True),
                    metadata=row,
                )
            )
        return results
