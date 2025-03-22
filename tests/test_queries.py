import pytest

from nd2k import queries
from nd2k.types import OperationType, TradingPair
from .helpers import create_test_operation, create_test_trade


def test_is_successful_true() -> None:
	data = create_test_operation(status="Sucesso")
	assert queries.is_successful(data)


def test_is_successful_false() -> None:
	data = create_test_operation(status="Anything Else")
	assert not queries.is_successful(data)


def test_is_part_of_a_trade_buy() -> None:
	data = create_test_operation(type=OperationType.BUY)
	assert queries.is_part_of_a_trade(data)


def test_is_part_of_a_trade_sell() -> None:
	data = create_test_operation(type=OperationType.SELL)
	assert queries.is_part_of_a_trade(data)


def test_is_part_of_a_trade_trading_fee() -> None:
	data = create_test_operation(type=OperationType.TRADING_FEE)
	assert queries.is_part_of_a_trade(data)


def test_is_part_of_a_trade_deposit() -> None:
	data = create_test_operation(type=OperationType.DEPOSIT)
	assert not queries.is_part_of_a_trade(data)


def test_is_part_of_a_trade_withdraw() -> None:
	data = create_test_operation(type=OperationType.WITHDRAW)
	assert not queries.is_part_of_a_trade(data)


def test_is_part_of_a_trade_withdraw_fee() -> None:
	data = create_test_operation(type=OperationType.WITHDRAW_FEE)
	assert not queries.is_part_of_a_trade(data)


def test_is_completed_complete() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.quote_asset = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert queries.is_completed(tr)


def test_is_completed_no_trading_fee() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.quote_asset = create_test_operation()
	assert not queries.is_completed(tr)


def test_is_completed_no_quote_asset() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert not queries.is_completed(tr)


def test_is_completed_no_base_asset() -> None:
	tr = create_test_trade()
	tr.operations.quote_asset = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert not queries.is_completed(tr)


def test_is_completed_only_base_asset() -> None:
	tr = create_test_trade()
	tr.operations.base_asset = create_test_operation()
	assert not queries.is_completed(tr)


def test_is_completed_only_quote_asset() -> None:
	tr = create_test_trade()
	tr.operations.quote_asset = create_test_operation()
	assert not queries.is_completed(tr)


def test_is_completed_only_trading_fee() -> None:
	tr = create_test_trade()
	tr.operations.trading_fee = create_test_operation()
	assert not queries.is_completed(tr)


def test_fits_as_base_asset_true() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert queries.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_already_has_base() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset = base

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert not queries.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_summary() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="SELL(FOO/BAR)", symbol="FOO")
	assert not queries.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert not queries.fits_as_base_asset(op, tr)


def test_fits_as_quote_asset_true() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert queries.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_already_has_quote() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert not queries.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_summary() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="SELL(FOO/BAR)", symbol="BAR")
	assert not queries.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_symbol() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert not queries.fits_as_quote_asset(op, tr)


def test_fits_as_trading_fee_already_has_fee() -> None:
	tr = create_test_trade()
	tr.operations.trading_fee = create_test_operation()
	op = create_test_operation(type=OperationType.TRADING_FEE)
	assert not queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell_wrong_type() -> None:
	tr = create_test_trade()
	op = create_test_operation(type=OperationType.WITHDRAW_FEE)
	assert not queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_buy() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.BUY)
	quote = create_test_operation(symbol="BAR", type=OperationType.BUY)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="FOO", type=OperationType.TRADING_FEE)
	assert queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_buy_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.BUY)
	quote = create_test_operation(symbol="BAR", type=OperationType.BUY)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="BAR", type=OperationType.TRADING_FEE)
	assert not queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.SELL)
	quote = create_test_operation(symbol="BAR", type=OperationType.SELL)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="BAR", type=OperationType.TRADING_FEE)
	assert queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.SELL)
	quote = create_test_operation(symbol="BAR", type=OperationType.SELL)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="FOO", type=OperationType.TRADING_FEE)
	assert not queries.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_empty_trade() -> None:
	tr = create_test_trade()
	op = create_test_operation(type=OperationType.TRADING_FEE)

	with pytest.raises(ValueError) as e:
		queries.fits_as_trading_fee(op, tr)

	assert str(e.value) == "Empty Trade"


def test_fits_as_trading_fee_malformed_trade() -> None:
	wrong_op = create_test_operation(type=OperationType.DEPOSIT)
	tr = create_test_trade()
	tr.operations.base_asset = wrong_op

	op = create_test_operation(type=OperationType.TRADING_FEE)

	with pytest.raises(ValueError) as e:
		queries.fits_as_trading_fee(op, tr)

	assert str(e.value) == "Malformed Trade"
