import pytest

from datetime import datetime, timedelta
from decimal import Decimal
from typing import cast

from nd2k.trade import Trade, PartialTrade, TradingPair, combine
from nd2k.operation import OperationType
from nd2k.transaction import Transaction, group_by_timestamp

from .helpers import fake_op, fake_partial_trade


def test_create_trading_pair_from_string() -> None:
	pair = TradingPair.from_string("Compra(DOGE/BRL)")
	assert pair.base  == "DOGE"
	assert pair.quote == "BRL"


def test_create_trading_pair_invalid_string() -> None:
	string = "AnythingElse"
	with pytest.raises(ValueError) as e:
		TradingPair.from_string(string)
	assert str(e.value) == f"No trading pair found in \"{string}\""


def test_create_partial_trade_from_base_asset() -> None:
	base = fake_op(
		summary = "Compra(ABC/XYZ)",
		type    = OperationType.BUY,
		symbol  = "ABC"
	)
	actual   = PartialTrade.from_operation(base)
	expected = PartialTrade(
		summary      = "Compra(ABC/XYZ)",
		trading_pair = TradingPair("ABC", "XYZ"),
		base_asset   = base,
	)
	assert actual == expected


def test_create_partial_trade_from_quote_asset() -> None:
	quote = fake_op(
		summary = "Compra(ABC/XYZ)",
		type    = OperationType.BUY,
		symbol  = "XYZ"
	)
	actual   = PartialTrade.from_operation(quote)
	expected = PartialTrade(
		summary      = "Compra(ABC/XYZ)",
		trading_pair = TradingPair("ABC", "XYZ"),
		quote_asset  = quote,
	)
	assert actual == expected


def test_is_completed() -> None:
	assert fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = None,
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = fake_op(),
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = None,
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = None,
	).is_completed()

	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = None,
		trading_fee = fake_op(),
	).is_completed()


def test_fits_as_base_asset() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert tr.fits_as_base_asset(op)


def test_fits_as_base_asset_already_has_base() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_base_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_base_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_quote_asset() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_already_has_quote() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_trading_fee_buy() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_already_has_fee() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	)
	fee = fake_op(type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell_wrong_type() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.WITHDRAW_FEE)
	assert not tr.fits_as_trading_fee(op)


def test_fits_as_trading_fee_buy_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_empty_trade() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		tr.fits_as_trading_fee(op)
	assert str(e.value) == "Empty Trade"


def test_fits_as_trading_fee_malformed_trade() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(type=OperationType.CRYPTO_DEPOSIT),
	)
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		tr.fits_as_trading_fee(op)
	assert str(e.value) == "Malformed Trade"


def test_combine() -> None:
	trades   = example_trades()
	groups   = group_by_timestamp(cast(list[Transaction], trades)).values()
	combined = [combine(cast(list[Trade], g)) for g in groups]

	assert len(combined) == 5

	# t0+t1
	assert combined[0].base_asset.amount  == Decimal("30") # 11+19
	assert combined[0].quote_asset.amount == Decimal("36") # 13+23
	assert combined[0].trading_fee.amount == Decimal("46") # 17+29

	# t2+t3
	assert combined[1].base_asset.amount  == Decimal("74") # 31+43
	assert combined[1].quote_asset.amount == Decimal("84") # 37+47
	assert combined[1].trading_fee.amount == Decimal("94") # 41+53

	assert combined[2] == trades[4] # t4

	# t5+t7
	assert combined[3].base_asset.amount  == Decimal("172") # 71+101
	assert combined[3].quote_asset.amount == Decimal("176") # 73+103
	assert combined[3].trading_fee.amount == Decimal("186") # 79+107

	assert combined[4] == trades[6] # t6


def example_trades() -> list[Trade]:
	now = datetime.now()
	a_minute_ago = now - timedelta(minutes=1)

	t0 = trade("BUY", "Buy(AAA/USD)", "AAA", "USD", now)
	t0.base_asset.amount  = Decimal("11")
	t0.quote_asset.amount = Decimal("13")
	t0.trading_fee.amount = Decimal("17")

	t1 = trade("BUY", "Buy(AAA/USD)", "AAA", "USD", now)
	t1.base_asset.amount  = Decimal("19")
	t1.quote_asset.amount = Decimal("23")
	t1.trading_fee.amount = Decimal("29")

	t2 = trade("SELL", "Sell(AAA/USD)", "AAA", "USD", now)
	t2.base_asset.amount  = Decimal("31")
	t2.quote_asset.amount = Decimal("37")
	t2.trading_fee.amount = Decimal("41")

	t3 = trade("SELL", "Sell(AAA/USD)", "AAA", "USD", now)
	t3.base_asset.amount  = Decimal("43")
	t3.quote_asset.amount = Decimal("47")
	t3.trading_fee.amount = Decimal("53")

	t4 = trade("BUY", "Buy(AAA/USD)", "AAA", "USD", a_minute_ago)
	t4.base_asset.amount  = Decimal("59")
	t4.quote_asset.amount = Decimal("61")
	t4.trading_fee.amount = Decimal("67")

	t5 = trade("BUY", "Buy(BBB/USD)", "BBB", "USD", now)
	t5.base_asset.amount  = Decimal("71")
	t5.quote_asset.amount = Decimal("73")
	t5.trading_fee.amount = Decimal("79")

	t6 = trade("BUY", "Buy(BBB/USD)", "BBB", "USD", a_minute_ago)
	t6.base_asset.amount  = Decimal("83")
	t6.quote_asset.amount = Decimal("89")
	t6.trading_fee.amount = Decimal("97")

	t7 = trade("BUY", "Buy(BBB/USD)", "BBB", "USD", now)
	t7.base_asset.amount  = Decimal("101")
	t7.quote_asset.amount = Decimal("103")
	t7.trading_fee.amount = Decimal("107")

	return [t for t in [t0, t1, t2, t3, t4, t5, t6, t7]]


def trade(ot: str, s: str, b: str, q: str, d: datetime) -> Trade:
	t = fake_partial_trade()

	t.summary = s
	t.trading_pair = TradingPair(b, q)

	t.base_asset = fake_op()
	t.base_asset.date    = d
	t.base_asset.type    = OperationType[ot]
	t.base_asset.summary = s
	t.base_asset.symbol  = b
	t.base_asset.amount  = Decimal("0")

	t.quote_asset = fake_op()
	t.quote_asset.date    = d
	t.quote_asset.type    = OperationType[ot]
	t.quote_asset.summary = s
	t.quote_asset.symbol  = q
	t.quote_asset.amount  = Decimal("0")

	t.trading_fee = fake_op()
	t.trading_fee.date    = d
	t.trading_fee.type    = OperationType.TRADING_FEE
	t.trading_fee.summary = "trading fee"
	t.trading_fee.symbol  = b if ot == "BUY" else q
	t.trading_fee.amount  = Decimal("0")

	return t.complete()
