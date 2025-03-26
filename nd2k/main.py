import sys
import os
import csv

from typing import cast
from . import utils, queries as q
from .types import Operation, Trade, NonTrade


csv_type = list[list[str]]


def entrypoint() -> None:
	if len(sys.argv) != 2:
		print("Usage: nd2k <novadax-csv>")
		exit(1)

	input_file = sys.argv[1]

	if not os.path.exists(input_file):
		print(f"Error: No such file: {input_file}")
		exit(1)

	lines = read_input_file(input_file)
	trades, non_trades = organize(lines)

	output_file = utils.output_filename(input_file, "koinly_trades")
	formatted   = format_trades(trades)
	write_output_file(output_file, formatted)

	output_file = utils.output_filename(input_file, "koinly_non_trades")
	formatted   = format_non_trades(non_trades)
	write_output_file(output_file, formatted)


def read_input_file(input_file: str) -> csv_type:
	with open(input_file, "r", encoding="utf-8", errors="ignore") as file:
		return list(csv.reader(file))


def write_output_file(output_file: str, contents: csv_type) -> None:
	with open(output_file, "w", encoding="utf-8", newline="\n") as file:
		writer = csv.writer(file)
		writer.writerows(contents)


def organize(lines: csv_type) -> tuple[ list[Trade], list[NonTrade] ]:
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


def format_trades(trades: list[Trade]) -> csv_type:
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
			base_asset.type.name,                       # Side
			f"{base_asset.amount}",                     # Amount
			f"{quote_asset.amount}",                    # Total
			f"{trading_fee.amount}",                    # Fee Amount
			trading_fee.symbol,                         # Fee Currency
			"",                                         # Order ID
			"",                                         # Trade ID
		])
	return lines


def format_non_trades(non_trades: list[NonTrade]) -> csv_type:
	lines = []
	lines.append(["Koinly Date", "Amount", "Currency", "Label", "TxHash"])
	for nt in non_trades:
		op = nt.operation

		lines.append([
			utils.format_date(op.date), # Koinly Date
			f"{op.amount}",             # Amount
			op.symbol,                  # Currency
			utils.koinly_tag(op.type),  # Tag
			"",                         # TxHash
		])
	return lines
