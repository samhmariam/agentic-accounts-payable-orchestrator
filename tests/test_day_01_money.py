from decimal import Decimal

import pytest

from aegisap.day_01.normalizers import parse_money


def test_parse_eur_locale_amount():
    assert parse_money("1.250,00 EUR") == Decimal("1250.00")
    assert parse_money("EUR 1250") == Decimal("1250.00")


def test_parse_gbp_plain_amount():
    assert parse_money("1500.00 GBP") == Decimal("1500.00")
    assert parse_money("GBP 1500.00") == Decimal("1500.00")


def test_ambiguous_single_separator_amount_is_rejected():
    with pytest.raises(ValueError, match="ambiguous amount"):
        parse_money("1.250")

    with pytest.raises(ValueError, match="ambiguous amount"):
        parse_money("1,250")


def test_amount_with_embedded_ocr_letter_is_rejected():
    with pytest.raises(ValueError, match="invalid amount format"):
        parse_money("1O0.00 USD")
