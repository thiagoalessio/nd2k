from datetime import datetime, timedelta
from decimal import Decimal
from typing import cast

from nd2k.converter import combine_by_timestamp
from nd2k.types import OperationType, Trade, TradingPair, NonTrade
from ..helpers import fake_op, fake_partial_trade

def test_combine_by_timestamp() -> None:
	trades     = example_trades()
	non_trades = example_non_trades()
	combined   = combine_by_timestamp(trades + non_trades)

	# t0+t1 | t2 | t3+t4 | t5+t7 | t6 | o0+o1 | o2 | o3 | o4 | o5+o7 | o6
	assert len(combined) == 11

	# t0+t1
	assert cast(Trade, combined[0]).base_asset.amount  == Decimal("30") # 11+19
	assert cast(Trade, combined[0]).quote_asset.amount == Decimal("36") # 13+23
	assert cast(Trade, combined[0]).trading_fee.amount == Decimal("46")  # 17+29

	# t2+t3
	assert cast(Trade, combined[1]).base_asset.amount  == Decimal("74") # 31+43
	assert cast(Trade, combined[1]).quote_asset.amount == Decimal("84") # 37+47
	assert cast(Trade, combined[1]).trading_fee.amount == Decimal("94")  # 41+53

	assert combined[2] == trades[4] # t4

	# t5+t7
	assert cast(Trade, combined[3]).base_asset.amount  == Decimal("172") # 71+101
	assert cast(Trade, combined[3]).quote_asset.amount == Decimal("176") # 73+103
	assert cast(Trade, combined[3]).trading_fee.amount == Decimal("186")  # 79+107

	assert combined[4] == trades[6] # t6

	# o0+o1
	assert cast(NonTrade, combined[5]).operation.amount  == Decimal("5") # 2+3

	assert combined[6] == non_trades[2] # o2
	assert combined[7] == non_trades[3] # o3
	assert combined[8] == non_trades[4] # o4

	# o5+o7
	assert cast(NonTrade, combined[9]).operation.amount  == Decimal("32") # 13+19

	assert combined[10] == non_trades[6] #o6

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


def example_non_trades() -> list[NonTrade]:
	now = datetime.now()
	a_minute_ago = now - timedelta(minutes=1)

	o0 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("2"),  date=now)
	o1 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("3"),  date=now)
	o2 = fake_op(summary="withdraw", symbol="BBB", amount=Decimal("5"),  date=now)
	o3 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("7"),  date=a_minute_ago)
	o4 = fake_op(summary="deposit",  symbol="AAA", amount=Decimal("11"), date=now)
	o5 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("13"), date=now)
	o6 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("17"), date=a_minute_ago)
	o7 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("19"), date=now)

	return [NonTrade(operation=o) for o in [o0, o1, o2, o3, o4, o5, o6, o7]]


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
