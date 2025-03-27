from datetime import datetime
from nd2k import formatter
from nd2k.types import OperationType


def test_format_date() -> None:
	data     = datetime(1970, 3, 15, 23, 45, 56)
	actual   = formatter.format_date(data)
	expected = "1970-03-15 23:45:56"
	assert actual == expected


def test_koinly_tag_crypto_deposit() -> None:
	assert "deposit" == formatter.koinly_tag(OperationType.CRYPTO_DEPOSIT)


def test_koinly_tag_fiat_deposit() -> None:
	assert "deposit" == formatter.koinly_tag(OperationType.FIAT_DEPOSIT)


def test_koinly_tag_crypto_withdraw() -> None:
	assert "withdraw" == formatter.koinly_tag(OperationType.CRYPTO_WITHDRAW)


def test_koinly_tag_withdraw_fee() -> None:
	assert "fee" == formatter.koinly_tag(OperationType.WITHDRAW_FEE)


def test_koinly_tag_redeemed_bonus() -> None:
	assert "reward" == formatter.koinly_tag(OperationType.REDEEMED_BONUS)


def test_koinly_tag_buy() -> None:
	assert "trade" == formatter.koinly_tag(OperationType.BUY)


def test_koinly_tag_sell() -> None:
	assert "trade" == formatter.koinly_tag(OperationType.SELL)


def test_koinly_tag_trading_fee() -> None:
	assert "fee" == formatter.koinly_tag(OperationType.TRADING_FEE)
