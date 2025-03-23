import pytest

from datetime import datetime
from decimal import Decimal
from nd2k import utils
from nd2k.types import (
	Operation,
	OperationType,
	Trade,
	TradeOperations,
	TradingPair,
)
from .helpers import create_test_operation


def test_output_filename() -> None:
	data     = "myfile.csv", "koinly_trades"
	actual   = utils.output_filename(*data)
	expected = "myfile_koinly_trades.csv"
	assert actual == expected


def test_parse_date() -> None:
	data     = "15/03/1970 23:45:56"
	actual   = utils.parse_date(data)
	expected = datetime(1970, 3, 15, 23, 45, 56)
	assert actual == expected


def test_format_date() -> None:
	data     = datetime(1970, 3, 15, 23, 45, 56)
	actual   = utils.format_date(data)
	expected = "1970-03-15 23:45:56"
	assert actual == expected


def test_parse_trading_pair() -> None:
	data     = "Compra(PANDORA/BRL)"
	actual   = utils.parse_trading_pair(data)
	expected = TradingPair(base="PANDORA", quote="BRL")
	assert actual == expected


def test_format_trading_pair() -> None:
	data     = TradingPair(base="PANDORA", quote="BRL")
	actual   = utils.format_trading_pair(data)
	expected = "PANDORA/BRL"
	assert actual == expected


def test_parse_trading_pair_invalid() -> None:
	data = "AnythingElse"

	with pytest.raises(ValueError) as e:
		utils.parse_trading_pair(data)

	assert str(e.value) == f"No trading pair found in \"{data}\""


def test_parse_amount_no_commas() -> None:
	data     = "+12345678901234567890 SHIB(≈R$0)"
	actual   = utils.parse_amount(data)
	expected = Decimal(12345678901234567890)
	assert actual == expected


def test_parse_amount_one_comma() -> None:
	data     = "R$ -355,77"
	actual   = utils.parse_amount(data)
	expected = Decimal("355.77")
	assert actual == expected


def test_parse_amount_multiple_commas() -> None:
	data     = "-121,162,430,769,2304 BABYDOGE2(≈R$0.45)"
	actual   = utils.parse_amount(data)
	expected = Decimal("121162430769.2304")
	assert actual == expected


def test_parse_amount_invalid() -> None:
	data = "No digits present in string"

	with pytest.raises(ValueError) as e:
		utils.parse_amount(data)

	assert str(e.value) == f"No numeric values found in \"{data}\""


def test_create_operation() -> None:
	csv_line = [
		"15/03/1970 23:45:56",
		"Compra(ABC/BRL)",
		"ABC",
		"-1,234,567 ABC(≈R$87.38)",
		"Sucesso",
	]
	actual   = utils.create_operation(csv_line)
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
	actual   = utils.create_trade(base)
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
	actual   = utils.create_trade(quote)
	expected = Trade(
		summary      = "Compra(ABC/XYZ)",
		operations   = TradeOperations(quote_asset=quote),
		trading_pair = TradingPair("ABC", "XYZ")
	)
	assert actual == expected
