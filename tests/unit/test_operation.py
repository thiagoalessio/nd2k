import pytest

from datetime import datetime
from decimal import Decimal

from nd2k.operation import OperationType, Operation
from .helpers import fake_op


def test_parse_date() -> None:
	data     = "15/03/1970 23:45:56"
	actual   = Operation.parse_date(data)
	expected = datetime(1970, 3, 15, 23, 45, 56)
	assert actual == expected


def test_parse_amount_no_commas() -> None:
	data     = "+12345678901234567890 SHIB(≈R$0)"
	actual   = Operation.parse_amount(data)
	expected = Decimal(12345678901234567890)
	assert actual == expected


def test_parse_amount_one_comma() -> None:
	data     = "R$ -355,77"
	actual   = Operation.parse_amount(data)
	expected = Decimal("355.77")
	assert actual == expected


def test_parse_amount_multiple_commas() -> None:
	data     = "-121,162,430,769,2304 BABYDOGE2(≈R$0.45)"
	actual   = Operation.parse_amount(data)
	expected = Decimal("121162430769.2304")
	assert actual == expected


def test_parse_amount_invalid() -> None:
	data = "No digits present in string"
	with pytest.raises(ValueError) as e:
		Operation.parse_amount(data)
	assert str(e.value) == f"No numeric values found in \"{data}\""


def test_create_operation_from_csv_row() -> None:
	row = [
		"15/03/1970 23:45:56",
		"Compra(ABC/BRL)",
		"ABC",
		"-1,234,567 ABC(≈R$87.38)",
		"Sucesso",
	]
	actual   = Operation.from_csv_row(row)
	expected = Operation(
		date    = datetime(1970, 3, 15, 23, 45, 56),
		type    = OperationType.BUY,
		summary = "Compra(ABC/BRL)",
		symbol  = "ABC",
		amount  = Decimal("1234.567"),
		status  = "Sucesso",
	)
	assert actual == expected


def test_is_successful() -> None:
	assert fake_op(status="Sucesso").is_successful()
	assert not fake_op(status="Other").is_successful()


def test_is_a_non_trade() -> None:
	assert not fake_op(type=OperationType.BUY).is_a_non_trade()
	assert not fake_op(type=OperationType.SELL).is_a_non_trade()
	assert not fake_op(type=OperationType.TRADING_FEE).is_a_non_trade()
	assert not fake_op(type=OperationType.SWAP).is_a_non_trade()

	assert fake_op(type=OperationType.CRYPTO_DEPOSIT).is_a_non_trade()
	assert fake_op(type=OperationType.FIAT_DEPOSIT).is_a_non_trade()
	assert fake_op(type=OperationType.CRYPTO_WITHDRAW).is_a_non_trade()
	assert fake_op(type=OperationType.FIAT_WITHDRAW).is_a_non_trade()
	assert fake_op(type=OperationType.WITHDRAW_FEE).is_a_non_trade()
	assert fake_op(type=OperationType.REDEEMED_BONUS).is_a_non_trade()
