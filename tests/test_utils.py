import pytest

from datetime import datetime
from tests.helpers import *
from nd2k.utils import *


def test_output_filename() -> None:
	data     = "myfile.csv", "koinly_trades"
	actual   = output_filename("myfile.csv", "koinly_trades")
	expected = "myfile_koinly_trades.csv"
	assert actual == expected


def test_parse_date() -> None:
	data     = "15/03/1970 23:45:56"
	actual   = parse_date(data)
	expected = datetime(1970, 3, 15, 23, 45, 56)
	assert actual == expected


def test_format_date() -> None:
	data     = datetime(1970, 3, 15, 23, 45, 56)
	actual   = format_date(data)
	expected = "1970-03-15 23:45:56"
	assert actual == expected


def test_parse_trading_pair() -> None:
	data     = "Compra(PANDORA/BRL)"
	actual   = parse_trading_pair(data)
	expected = TradingPair(base="PANDORA", quote="BRL")
	assert actual == expected


def test_format_trading_pair() -> None:
	data     = TradingPair(base="PANDORA", quote="BRL")
	actual   = format_trading_pair(data)
	expected = "PANDORA/BRL"
	assert actual == expected


def test_parse_trading_pair_invalid() -> None:
	data = "AnythingElse"

	with pytest.raises(ValueError) as e:
		parse_trading_pair(data)

	assert str(e.value) == f"No trading pair found in \"{data}\""


def test_parse_amount_no_commas() -> None:
	data     = "+12345678901234567890 SHIB(≈R$0)"
	actual   = parse_amount(data)
	expected = Decimal(12345678901234567890)
	assert actual == expected


def test_parse_amount_one_comma() -> None:
	data     = "R$ -355,77"
	actual   = parse_amount(data)
	expected = Decimal("355.77")
	assert actual == expected


def test_parse_amount_multiple_commas() -> None:
	data     = "-121,162,430,769,2304 BABYDOGE2(≈R$0.45)"
	actual   = parse_amount(data)
	expected = Decimal("121162430769.2304")
	assert actual == expected


def test_parse_amount_invalid() -> None:
	data = "No digits present in string"

	with pytest.raises(ValueError) as e:
		parse_amount(data)

	assert str(e.value) == f"No numeric values found in \"{data}\""


def test_is_successful_true() -> None:
	data = create_test_operation(status="Sucesso")
	assert is_successful(data)


def test_is_successful_false() -> None:
	data = create_test_operation(status="Anything Else")
	assert not is_successful(data)


def test_is_part_of_a_trade_buy() -> None:
	data = create_test_operation(type=OperationType.BUY)
	assert is_part_of_a_trade(data)


def test_is_part_of_a_trade_sell() -> None:
	data = create_test_operation(type=OperationType.SELL)
	assert is_part_of_a_trade(data)


def test_is_part_of_a_trade_trading_fee() -> None:
	data = create_test_operation(type=OperationType.TRADING_FEE)
	assert is_part_of_a_trade(data)


def test_is_part_of_a_trade_deposit() -> None:
	data = create_test_operation(type=OperationType.DEPOSIT)
	assert not is_part_of_a_trade(data)


def test_is_part_of_a_trade_withdraw() -> None:
	data = create_test_operation(type=OperationType.WITHDRAW)
	assert not is_part_of_a_trade(data)


def test_is_part_of_a_trade_withdraw_fee() -> None:
	data = create_test_operation(type=OperationType.WITHDRAW_FEE)
	assert not is_part_of_a_trade(data)


def test_is_completed_complete() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.quote_asset = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert is_completed(tr)


def test_is_completed_no_trading_fee() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.quote_asset = create_test_operation()
	assert not is_completed(tr)


def test_is_completed_no_quote_asset() -> None:
	tr = create_test_trade()
	tr.operations.base_asset  = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert not is_completed(tr)


def test_is_completed_no_base_asset() -> None:
	tr = create_test_trade()
	tr.operations.quote_asset = create_test_operation()
	tr.operations.trading_fee = create_test_operation()
	assert not is_completed(tr)


def test_is_completed_only_base_asset() -> None:
	tr = create_test_trade()
	tr.operations.base_asset = create_test_operation()
	assert not is_completed(tr)


def test_is_completed_only_quote_asset() -> None:
	tr = create_test_trade()
	tr.operations.quote_asset = create_test_operation()
	assert not is_completed(tr)


def test_is_completed_only_trading_fee() -> None:
	tr = create_test_trade()
	tr.operations.trading_fee = create_test_operation()
	assert not is_completed(tr)


def test_fits_as_base_asset_true() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert fits_as_base_asset(op, tr)


def test_fits_as_base_asset_already_has_base() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset = base

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert not fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_summary() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="SELL(FOO/BAR)", symbol="FOO")
	assert not fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	fee   = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert not fits_as_base_asset(op, tr)


def test_fits_as_quote_asset_true() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_already_has_quote() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	quote = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.quote_asset = quote

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="BAR")
	assert not fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_summary() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="SELL(FOO/BAR)", symbol="BAR")
	assert not fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_symbol() -> None:
	pair = TradingPair(base="FOO", quote="BAR")
	base = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	fee  = create_test_operation()

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.trading_fee = fee

	op = create_test_operation(summary="BUY(FOO/BAR)", symbol="FOO")
	assert not fits_as_quote_asset(op, tr)


def test_fits_as_trading_fee_already_has_fee() -> None:
	tr = create_test_trade()
	tr.operations.trading_fee = create_test_operation()
	op = create_test_operation(type=OperationType.TRADING_FEE)
	assert not fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell_wrong_type() -> None:
	tr = create_test_trade()
	op = create_test_operation(type=OperationType.WITHDRAW_FEE)
	assert not fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_buy() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.BUY)
	quote = create_test_operation(symbol="BAR", type=OperationType.BUY)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="FOO", type=OperationType.TRADING_FEE)
	assert fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_buy_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.BUY)
	quote = create_test_operation(symbol="BAR", type=OperationType.BUY)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="BAR", type=OperationType.TRADING_FEE)
	assert not fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.SELL)
	quote = create_test_operation(symbol="BAR", type=OperationType.SELL)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="BAR", type=OperationType.TRADING_FEE)
	assert fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_sell_wrong_symbol() -> None:
	pair  = TradingPair(base="FOO", quote="BAR")
	base  = create_test_operation(symbol="FOO", type=OperationType.SELL)
	quote = create_test_operation(symbol="BAR", type=OperationType.SELL)

	tr = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	tr.operations.base_asset  = base
	tr.operations.quote_asset = quote

	op = create_test_operation(symbol="FOO", type=OperationType.TRADING_FEE)
	assert not fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_empty_trade() -> None:
	tr = create_test_trade()
	op = create_test_operation(type=OperationType.TRADING_FEE)

	with pytest.raises(ValueError) as e:
		fits_as_trading_fee(op, tr)

	assert str(e.value) == "Empty Trade"


def test_fits_as_trading_fee_malformed_trade() -> None:
	wrong_op = create_test_operation(type=OperationType.DEPOSIT)
	tr = create_test_trade()
	tr.operations.base_asset = wrong_op

	op = create_test_operation(type=OperationType.TRADING_FEE)

	with pytest.raises(ValueError) as e:
		fits_as_trading_fee(op, tr)

	assert str(e.value) == "Malformed Trade"


def test_create_operation() -> None:
	csv_line = [
		"15/03/1970 23:45:56",
		"Compra(ABC/BRL)",
		"ABC",
		"-1,234,567 ABC(≈R$87.38)",
		"Sucesso",
	]
	actual   = create_operation(csv_line)
	expected = Operation(
		date    = datetime(1970, 3, 15, 23, 45, 56),
		type    = OperationType.BUY,
		summary = "Compra(ABC/BRL)",
		symbol  = "ABC",
		amount  = Decimal("1234.567"),
		status  = "Sucesso",
	)
	assert actual == expected


def test_create_trade_from_base_asset() -> None:
	base = create_test_operation(
		summary = "Compra(ABC/XYZ)",
		type    = OperationType.BUY,
		symbol  = "ABC"
	)
	actual   = create_trade(base)
	expected = Trade(
		summary      = "Compra(ABC/XYZ)",
		operations   = TradeOperations(base_asset=base),
		trading_pair = TradingPair("ABC", "XYZ")
	)
	assert actual == expected


def test_create_trade_from_quote_asset() -> None:
	quote = create_test_operation(
		summary = "Compra(ABC/XYZ)",
		type    = OperationType.BUY,
		symbol  = "XYZ"
	)
	actual   = create_trade(quote)
	expected = Trade(
		summary      = "Compra(ABC/XYZ)",
		operations   = TradeOperations(quote_asset=quote),
		trading_pair = TradingPair("ABC", "XYZ")
	)
	assert actual == expected
