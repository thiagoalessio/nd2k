from datetime import datetime
from nd2k import formatter


def test_format_date() -> None:
	date = datetime(1970, 3, 15, 23, 45, 56)
	assert formatter.format_date(date) == "1970-03-15 23:45:56"


def test_koinly_tag() -> None:
	assert "deposit"  == formatter.koinly_tag("CRYPTO_DEPOSIT")
	assert "deposit"  == formatter.koinly_tag("FIAT_DEPOSIT")
	assert "withdraw" == formatter.koinly_tag("CRYPTO_WITHDRAW")
	assert "withdraw" == formatter.koinly_tag("FIAT_WITHDRAW")
	assert "fee"      == formatter.koinly_tag("WITHDRAW_FEE")
	assert "fee"      == formatter.koinly_tag("TRADING_FEE")
	assert "trade"    == formatter.koinly_tag("BUY")
	assert "trade"    == formatter.koinly_tag("SELL")
	assert "reward"   == formatter.koinly_tag("REDEEMED_BONUS")
	assert ""         == formatter.koinly_tag("ANYTHING_ELSE")
