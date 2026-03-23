from __future__ import annotations

from decimal import Decimal

HIGH_VALUE_THRESHOLD = Decimal("10000.00")
ROUTE_PRECEDENCE = ["high_value", "new_vendor", "clean_path"]
KNOWN_VENDORS = {"Contoso Ltd", "Rhein Energie GmbH"}
MODEL_PRICING = {
    "input_per_1k": 0.0010,
    "output_per_1k": 0.0020,
}
