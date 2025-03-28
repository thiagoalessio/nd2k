import pytest
from datetime import datetime
from decimal import Decimal
from nd2k.converter.organize_rows import (
	parse_date,
	parse_amount,
	parse_trading_pair,
	create_operation,
	create_partial_trade,
)
from nd2k.types import OperationType, PartialTrade, TradingPair, Operation
from ..helpers import fake_op


def test_parse_date() -> None:
	data     = "15/03/1970 23:45:56"
	actual   = parse_date(data)
	expected = datetime(1970, 3, 15, 23, 45, 56)
	assert actual == expected


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


def test_parse_trading_pair() -> None:
	data = "Compra(DOGE/BRL)"
	assert parse_trading_pair(data) == TradingPair(base="DOGE", quote="BRL")


def test_parse_trading_pair_invalid() -> None:
	data = "AnythingElse"
	with pytest.raises(ValueError) as e:
		parse_trading_pair(data)
	assert str(e.value) == f"No trading pair found in \"{data}\""


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


def test_create_partial_trade_from_base_asset() -> None:
	base = fake_op(
		summary = "Compra(ABC/XYZ)",
		type    = OperationType.BUY,
		symbol  = "ABC"
	)
	actual   = create_partial_trade(base)
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
	actual   = create_partial_trade(quote)
	expected = PartialTrade(
		summary      = "Compra(ABC/XYZ)",
		trading_pair = TradingPair("ABC", "XYZ"),
		quote_asset  = quote,
	)
	assert actual == expected
