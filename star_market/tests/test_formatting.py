import pytest

from utils.formatting import fmt_uzs


@pytest.mark.parametrize(
    "amount,expected",
    [(27399, "27 399 UZS"), (999, "999 UZS"), (35001999, "35 001 999 UZS"), (0, "0 UZS")],
)
def test_fmt_uzs(amount, expected):
    assert fmt_uzs(amount) == expected
