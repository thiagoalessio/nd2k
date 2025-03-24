import os
import filecmp
import pytest

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import Mock
from nd2k import main
from nd2k.types import (
	Operation,
	OperationType,
	NonTrade,
	Trade,
	TradeOperations,
	TradingPair,
)
from .helpers import create_test_operation, create_test_trade, normalize_file


def test_entrypoint_no_input_file(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k"])

	with pytest.raises(SystemExit) as exc_info:
		main.entrypoint()

	assert exc_info.value.code == 1
	assert "Usage: nd2k <novadax-csv>" in capsys.readouterr().out


def test_entrypoint_input_file_does_not_exist(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k", "invalid-file.csv"])

	with pytest.raises(SystemExit) as exc_info:
		main.entrypoint()

	assert exc_info.value.code == 1
	assert "Error: No such file: invalid-file.csv" in capsys.readouterr().out


def test_entrypoint_valid_input(monkeypatch: Any) -> None:
	input_file = "myfile.csv"
	with open(input_file, "w"):
		pass

	mock_convert = Mock()
	monkeypatch.setattr("nd2k.main.convert", mock_convert)
	monkeypatch.setattr("sys.argv", ["nd2k", input_file])

	main.entrypoint()
	mock_convert.assert_called_once_with(input_file)
	os.remove(input_file)


def test_convert() -> None:
	input_file = "tests/sample_data/novadax.csv"
	main.convert(input_file)

	actual   = "tests/sample_data/novadax_koinly_trades.csv"
	expected = "tests/sample_data/koinly_trades.csv"
	normalize_file(actual)
	normalize_file(expected)
	assert filecmp.cmp(actual, expected, shallow=False)
	os.remove(actual)

	actual   = "tests/sample_data/novadax_koinly_non_trades.csv"
	expected = "tests/sample_data/koinly_non_trades.csv"
	normalize_file(actual)
	normalize_file(expected)
	assert filecmp.cmp(actual, expected, shallow=False)
	os.remove(actual)


def test_organize() -> None:
	tr1_ops = TradeOperations()
	tr1_ops.base_asset = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.BUY,
		summary = "Compra(XYZ/BRL)",
		symbol  = "XYZ",
		amount  = Decimal("3971.00"),
		status  = "Sucesso",
	)
	tr1_ops.quote_asset = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.BUY,
		summary = "Compra(XYZ/BRL)",
		symbol  = "BRL",
		amount  = Decimal("1.47"),
		status  = "Sucesso",
	)
	tr1_ops.trading_fee = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.TRADING_FEE,
		summary = "Taxa de transação",
		symbol  = "XYZ",
		amount  = Decimal("15.4869"),
		status  = "Sucesso",
	)
	trade1 = Trade(
		summary      = "Compra(XYZ/BRL)",
		operations   = tr1_ops,
		trading_pair = TradingPair(base="XYZ", quote="BRL"),
	)

	tr2_ops = TradeOperations()
	tr2_ops.base_asset = Operation(
		date   = datetime(2025, 3, 21, 15, 21, 47),
		type   = OperationType.SELL,
		summary= "Venda(ABC/USD)",
		symbol = "ABC",
		amount = Decimal("164083.00"),
		status = "Sucesso",
	)
	tr2_ops.quote_asset = Operation(
		date   = datetime(2025, 3, 21, 15, 21, 47),
		type   = OperationType.SELL,
		summary= "Venda(ABC/USD)",
		symbol = "USD",
		amount = Decimal("41.00"),
		status = "Sucesso",
	)
	tr2_ops.trading_fee = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 48),
		type    = OperationType.TRADING_FEE,
		summary = "Taxa de transação",
		symbol  = "USD",
		amount  = Decimal("0.05"),
		status  = "Sucesso",
	)
	trade2 = Trade(
		summary      = "Venda(ABC/USD)",
		operations   = tr2_ops,
		trading_pair = TradingPair(base="ABC", quote="USD"),
	)

	tr3_ops = TradeOperations()
	tr3_ops.base_asset = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 47),
		type    = OperationType.BUY,
		summary = "Compra(ABC/USD)",
		symbol  = "ABC",
		amount  = Decimal("1.4698"),
		status  = "Sucesso",
	)
	tr3_ops.quote_asset = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 48),
		type    = OperationType.BUY,
		summary = "Compra(ABC/USD)",
		symbol  = "USD",
		amount  = Decimal("100.86"),
		status  = "Sucesso",
	)
	tr3_ops.trading_fee = Operation(
		date    = datetime(2025, 3, 21, 15, 22, 0),
		type    = OperationType.TRADING_FEE,
		summary = "Taxa de transação",
		symbol  = "ABC",
		amount  = Decimal("0.00573222"),
		status  = "Sucesso",
	)
	trade3 = Trade(
		summary      = "Compra(ABC/USD)",
		operations   = tr3_ops,
		trading_pair = TradingPair(base="ABC", quote="USD"),
	)

	deposit = NonTrade(operation=Operation(
		date    = datetime(2024, 10, 7, 21, 0, 57),
		type    = OperationType.DEPOSIT,
		summary = "Depósito de criptomoedas",
		symbol  = "SUNWUKONG",
		amount  = Decimal("33848.30"),
		status  = "Sucesso",
	))

	withdraw = NonTrade(operation=Operation(
		date    = datetime(2025, 3, 20, 16, 19, 1),
		type    = OperationType.WITHDRAW,
		summary = "Saque de criptomoedas",
		symbol  = "DCR",
		amount  = Decimal("1.5446"),
		status  = "Sucesso",
	))

	trades, non_trades = main.organize(input_for_organize_tests)
	assert trades == [trade3, trade2, trade1]
	assert non_trades == [withdraw, deposit]


def test_organize_incomplete_trades() -> None:
	with pytest.raises(ValueError) as e:
		main.organize(input_for_organize_tests[0:4])
	assert str(e.value) == "Input has incomplete trades"


def test_create_or_update_trade_no_partial_trades() -> None:
	op = create_test_operation(
		type    = OperationType.BUY,
		summary = "Test(FOO/BAR)",
		symbol  = "FOO",
	)
	partial_trades: list[Trade] = []
	tr = main.create_or_update_trade(op, partial_trades)
	assert tr.operations.base_asset == op
	assert [tr] == partial_trades


def test_create_or_update_trade_no_matches() -> None:
	op   = create_test_operation(summary="(FOO/BAR)", symbol="FOO", type=OperationType.BUY)
	pair = TradingPair(base="ABC", quote="XYZ")
	tr1  = create_test_trade(summary="(ABC/XYZ)", trading_pair=pair)
	base = create_test_operation(symbol="ABC", type=OperationType.BUY)
	tr1.operations.quote_asset = base

	partial_trades = [tr1]

	tr2 = main.create_or_update_trade(op, partial_trades)
	assert tr2.operations.base_asset == op
	assert partial_trades == [tr1, tr2]


def test_create_or_update_trade_fits_as_base() -> None:
	op    = create_test_operation(summary="Test", symbol="FOO", type=OperationType.BUY)
	pair  = TradingPair(base="FOO", quote="BAR")
	tr1   = create_test_trade(summary="Test", trading_pair=pair)
	quote = create_test_operation(symbol="FOO", type=OperationType.BUY)
	tr1.operations.quote_asset = quote

	tr2 = main.create_or_update_trade(op, [tr1])
	assert tr1 == tr2
	assert tr2.operations.base_asset == op


def test_create_or_update_trade_fits_as_quote() -> None:
	op   = create_test_operation(summary="Test", symbol="BAR", type=OperationType.BUY)
	pair = TradingPair(base="FOO", quote="BAR")
	tr1  = create_test_trade(summary="Test", trading_pair=pair)
	base = create_test_operation(symbol="FOO", type=OperationType.BUY)
	tr1.operations.base_asset = base

	tr2 = main.create_or_update_trade(op, [tr1])
	assert tr1 == tr2
	assert tr2.operations.quote_asset == op


def test_create_or_update_trade_fits_as_fee() -> None:
	op   = create_test_operation(symbol="FOO", type=OperationType.TRADING_FEE)
	pair = TradingPair(base="FOO", quote="BAR")
	tr1  = create_test_trade(summary="BUY(FOO/BAR)", trading_pair=pair)
	base = create_test_operation(symbol="FOO", type=OperationType.BUY)
	tr1.operations.base_asset = base

	tr2 = main.create_or_update_trade(op, [tr1])
	assert tr1 == tr2
	assert tr2.operations.trading_fee == op


def test_format_trades() -> None:
	tr1_ops = TradeOperations()
	tr1_ops.base_asset = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.BUY,
		summary = "Compra(XYZ/BRL)",
		symbol  = "XYZ",
		amount  = Decimal("3971.00"),
		status  = "Sucesso",
	)
	tr1_ops.quote_asset = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.BUY,
		summary = "Compra(XYZ/BRL)",
		symbol  = "BRL",
		amount  = Decimal("1.47"),
		status  = "Sucesso",
	)
	tr1_ops.trading_fee = Operation(
		date    = datetime(2025, 3, 20, 0, 0, 0),
		type    = OperationType.TRADING_FEE,
		summary = "Taxa de transação",
		symbol  = "XYZ",
		amount  = Decimal("15.4869"),
		status  = "Sucesso",
	)
	trade1 = Trade(
		summary      = "Compra(XYZ/BRL)",
		operations   = tr1_ops,
		trading_pair = TradingPair(base="XYZ", quote="BRL"),
	)

	tr2_ops = TradeOperations()
	tr2_ops.base_asset = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 47),
		type    = OperationType.SELL,
		summary = "Venda(ABC/USD)",
		symbol  = "ABC",
		amount  = Decimal("164083.00"),
		status  = "Sucesso",
	)
	tr2_ops.quote_asset = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 47),
		type    = OperationType.SELL,
		summary = "Venda(ABC/USD)",
		symbol  = "USD",
		amount  = Decimal("41.00"),
		status  = "Sucesso",
	)
	tr2_ops.trading_fee = Operation(
		date    = datetime(2025, 3, 21, 15, 21, 48),
		type    = OperationType.TRADING_FEE,
		summary = "Taxa de transação",
		symbol  = "USD",
		amount  = Decimal("0.05"),
		status  = "Sucesso",
	)
	trade2 = Trade(
		summary      = "Venda(ABC/USD)",
		operations   = tr2_ops,
		trading_pair = TradingPair(base="ABC", quote="USD"),
	)

	assert main.format_trades([trade1, trade2]) == expected_format_trade_result


def test_format_non_trades() -> None:
	deposit = NonTrade(operation=Operation(
		date   = datetime(2024, 10, 27, 0, 14, 54),
		summary= "Depósito de criptomoedas",
		type   = OperationType.DEPOSIT,
		symbol = "ALITA",
		amount = Decimal("18490811.57243999"),
		status = "Sucesso",
	))
	withdraw = NonTrade(operation=Operation(
		date   = datetime(2025, 3, 20, 16, 19, 1),
		type   = OperationType.WITHDRAW,
		summary= "Saque de criptomoedas",
		symbol = "DCR",
		amount = Decimal("1.5446"),
		status = "Sucesso",
	))

	assert main.format_non_trades([deposit, withdraw]) == expected_format_non_trades_result


input_for_organize_tests = [
# Headers
["(UTC)HistoryTrade", "Tipo", "Moeda", "Valor", "Status"],

# Trades 2 & 3 mixed up
["21/3/2025 15:22:00", "Taxa de transação", "ABC", "-0,00573222 ABC(≈$0.39)", "Sucesso"],
["21/3/2025 15:21:48", "Compra(ABC/USD)",   "USD", "$ -100,86",               "Sucesso"],
["21/3/2025 15:21:48", "Compra(ABC/USD)",   "USD", "$ -100,86",               "Falha"],
["21/3/2025 15:21:48", "Taxa de transação", "USD", "$ -0,05",                 "Sucesso"],
["21/3/2025 15:21:47", "Compra(ABC/USD)",   "ABC", "+1,4698 ABC(≈$100.87)",   "Sucesso"],
["21/3/2025 15:21:47", "Venda(ABC/USD)",    "ABC", "-164,083,00 ABC(≈$41)",   "Sucesso"],
["21/3/2025 15:21:47", "Venda(ABC/USD)",    "USD", "$ +41,00",                "Sucesso"],

# Trade 1 operations mixed up with a withdraw operation
["20/3/2025 00:00:00", "Taxa de transação",     "XYZ", "-15,4869 XYZ(≈R$0.01)",  "Sucesso"],
["20/3/2025 16:19:01", "Saque de criptomoedas", "DCR", "-1,5446 DCR(≈R$1.55)",   "Sucesso"],
["20/3/2025 00:00:00", "Compra(XYZ/BRL)",       "BRL", "R$ -1,47",               "Sucesso"],
["20/3/2025 00:00:00", "Compra(XYZ/BRL)",       "XYZ", "+3,971,00 XYZ(≈R$1.48)", "Sucesso"],

# Deposit operation
["07/10/2024 21:00:57", "Depósito de criptomoedas", "SUNWUKONG", "+33,848,30 SUNWUKONG(≈R$1320.08)", "Sucesso"],
]


expected_format_trade_result = [
["Koinly Date",         "Pair",    "Side", "Amount",    "Total", "Fee Amount", "Fee Currency", "Order ID", "Trade ID"],
["2025-03-20 00:00:00", "XYZ/BRL", "BUY",  "3971.00",   "1.47",  "15.4869",    "XYZ",          "",         ""],
["2025-03-21 15:21:47", "ABC/USD", "SELL", "164083.00", "41.00", "0.05",       "USD",          "",         ""]
]


expected_format_non_trades_result = [
["Koinly Date",         "Amount",            "Currency", "Label",   "TxHash"],
["2024-10-27 00:14:54", "18490811.57243999", "ALITA",    "DEPOSIT", ""],
["2025-03-20 16:19:01", "1.5446",            "DCR",      "WITHDRAW",""]
]
