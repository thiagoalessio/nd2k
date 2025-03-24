import sys
import os
import csv

from typing import cast
from . import utils, queries as q
from .types import Operation, Trade, NonTrade


def entrypoint() -> None:
	if len(sys.argv) != 2:
		print("Usage: nd2k <novadax-csv>")
		exit(1)

	novadax_csv = sys.argv[1]
	if not os.path.exists(novadax_csv):
		print(f"Error: No such file: {novadax_csv}")
		exit(1)

	convert(novadax_csv)


def convert(input_filename: str) -> None:
	with open(input_filename, "r") as file:
		lines = list(csv.reader(file))

	trades, non_trades = organize(lines)

	output = utils.output_filename(input_filename, "koinly_trades")
	with open(output, "w", encoding="utf-8", newline="\n") as file:
		writer = csv.writer(file)
		writer.writerows(format_trades(trades))

	output = utils.output_filename(input_filename, "koinly_non_trades")
	with open(output, "w", encoding="utf-8", newline="\n") as file:
		writer = csv.writer(file)
		writer.writerows(format_non_trades(non_trades))


def organize(lines: list[list[str]]) -> tuple[ list[Trade], list[NonTrade] ]:
	trades = []
	non_trades = []
	partial_trades: list[Trade] = []

	for line in reversed(lines[1:]):
		op = utils.create_operation(line)

		if not q.is_successful(op):
			continue

		if not q.is_part_of_a_trade(op):
			non_trades.append(NonTrade(operation=op))
			continue

		tr = create_or_update_trade(op, partial_trades)

		if q.is_completed(tr):
			trades.append(tr)
			partial_trades.remove(tr)

	if len(partial_trades):
		raise ValueError("Input has incomplete trades")

	return (
		list(reversed(trades)),
		list(reversed(non_trades)))


def create_or_update_trade(op: Operation, partial_trades: list[Trade]) -> Trade:
	for tr in partial_trades:
		if q.fits_as_base_asset(op, tr):
			tr.operations.base_asset = op
			return tr

		if q.fits_as_quote_asset(op, tr):
			tr.operations.quote_asset = op
			return tr

		if q.fits_as_trading_fee(op, tr):
			tr.operations.trading_fee = op
			return tr

	tr = utils.create_trade(op)
	partial_trades.append(tr)
	return tr


def format_trades(trades: list[Trade]) -> list[list[str]]:
	lines = []
	lines.append([
		"Koinly Date", "Pair", "Side", "Amount", "Total",
		"Fee Amount", "Fee Currency", "Order ID", "Trade ID",
	])
	for tr in trades:
		base_asset  = cast(Operation, tr.operations.base_asset)
		quote_asset = cast(Operation, tr.operations.quote_asset)
		trading_fee = cast(Operation, tr.operations.trading_fee)

		lines.append([
			utils.format_date(base_asset.date),         # Koinly Date
			utils.format_trading_pair(tr.trading_pair), # Pair
			base_asset.type.name,                 # Side
			f"{base_asset.amount}",               # Amount
			f"{quote_asset.amount}",              # Total
			f"{trading_fee.amount}",              # Fee Amount
			trading_fee.symbol,                   # Fee Currency
			"",                                   # Order ID
			"",                                   # Trade ID
		])
	return lines


def format_non_trades(non_trades: list[NonTrade]) -> list[list[str]]:
	lines = []
	lines.append(["Koinly Date", "Amount", "Currency", "Label", "TxHash"])
	for nt in non_trades:
		op = nt.operation

		lines.append([
			utils.format_date(op.date), # Koinly Date
			f"{op.amount}",       # Amount
			op.symbol,            # Currency
			op.type.name,         # Label -> HAS MEANING, CHECK DOCS
			"",                   # TxHash
		])
	return lines
