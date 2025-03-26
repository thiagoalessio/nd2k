import sys
import os
import csv

from decimal import Decimal
from typing import cast
from collections import defaultdict
from . import utils, queries as q
from .types import Operation, OperationType, Trade, NonTrade, Transaction, PartialTrade


csv_type = list[list[str]]


def entrypoint() -> None:
	if len(sys.argv) != 2:
		print("Usage: nd2k <novadax-csv>")
		exit(1)

	input_file = sys.argv[1]

	if not os.path.exists(input_file):
		print(f"Error: No such file: {input_file}")
		exit(1)

	result = utils.pipe(
		input_file,
		read_input_file,
		organize,
		combine,
		order_by_date,
		universal_format,
	)

	output_file = utils.output_filename(input_file, "koinly_universal")
	write_output_file(output_file, result)


def read_input_file(input_file: str) -> csv_type:
	with open(input_file, "r", encoding="utf-8", errors="ignore") as file:
		return list(csv.reader(file))


def organize(lines: csv_type) -> list[Transaction]:
	trades: list[Trade] = []
	non_trades: list[NonTrade] = []
	partial_trades: list[PartialTrade] = []

	for line in reversed(lines[1:]):
		op = utils.create_operation(line)

		if not q.is_successful(op):
			continue

		if not q.is_part_of_a_trade(op):
			non_trades.append(NonTrade(operation=op))
			continue

		tr = create_or_update_trade(op, partial_trades)

		if q.is_completed(tr):
			trades.append(tr.complete())
			partial_trades.remove(tr)

	if len(partial_trades):
		raise ValueError("Input has partial trades")

	return cast(list[Transaction], trades + non_trades)


def create_or_update_trade(op: Operation, partial_trades: list[PartialTrade]) -> PartialTrade:
	for tr in partial_trades:
		if q.fits_as_base_asset(op, tr):
			tr.base_asset = op
			return tr

		if q.fits_as_quote_asset(op, tr):
			tr.quote_asset = op
			return tr

		if q.fits_as_trading_fee(op, tr):
			tr.trading_fee = op
			return tr

	tr = utils.create_partial_trade(op)
	partial_trades.append(tr)
	return tr


def combine(transactions: list[Transaction]) -> list[Transaction]:
	groups = defaultdict(list)
	for t in transactions:
		idx = utils.combine_group_index(t)
		groups[idx].append(t)

	combined = []
	for g in groups.values():
		if q.is_trade(g[0]):
			t = combine_trades(cast(list[Trade], g))
		else:
			t = combine_non_trades(cast(list[NonTrade], g))
		combined.append(t)

	return combined


def combine_trades(lst: list[Trade]) -> Trade:
	base  = lst[0].base_asset
	quote = lst[0].quote_asset
	fee   = lst[0].trading_fee

	base.amount  = Decimal(sum(i.base_asset.amount  for i in lst))
	quote.amount = Decimal(sum(i.quote_asset.amount for i in lst))
	fee.amount   = Decimal(sum(i.trading_fee.amount for i in lst))

	trade = utils.create_trade(base, quote, fee)
	return trade


def combine_non_trades(lst: list[NonTrade]) -> NonTrade:
	op = lst[0].operation
	op.amount = Decimal(sum(i.operation.amount for i in lst))
	return NonTrade(operation=op)


def universal_format(transactions: list[Transaction]) -> csv_type:
	lines = []
	lines.append([
		"Date", "Sent Amount", "Sent Currency", "Received Amount",
		"Received Currency", "Fee Amount", "Fee Currency", "Net Worth Amount",
		"Net Worth Currency", "Label", "Description",
	])

	for t in transactions:
		if isinstance(t, Trade):
			lines.append(format_trade(t))
		else:
			lines.append(format_non_trade(t))

	return lines


def format_trade(t: Trade) -> list[str]:
	if t.base_asset.type == OperationType.BUY:
		sent_amount = t.quote_asset.amount
		sent_symbol = t.quote_asset.symbol
		recv_amount = t.base_asset.amount
		recv_symbol = t.base_asset.symbol
	else:
		sent_amount = t.base_asset.amount
		sent_symbol = t.base_asset.symbol
		recv_amount = t.quote_asset.amount
		recv_symbol = t.quote_asset.symbol

	return [
		utils.format_date(t.base_asset.date), # Date
		f"{sent_amount}",                   # Sent Amount
		f"{sent_symbol}",                   # Sent Currency
		f"{recv_amount}",                   # Received Amount
		f"{recv_symbol}",                   # Received Currency
		f"{t.trading_fee.amount}",          # Fee Amount
		f"{t.trading_fee.symbol}",          # Fee Currency
		"",                                 # Net Worth Amount
		"",                                 # Net Worth Currency
		utils.koinly_tag(t.base_asset.type), # Label
		"",                                 # Description
		"",                                 # TxHash
	]


def format_non_trade(t: NonTrade) -> list[str]:
	op = t.operation

	if op.type.name in ["CRYPTO_WITHDRAW", "FIAT_WITHDRAW", "WITHDRAW_FEE"]:
		sent_amount = str(op.amount)
		sent_symbol = str(op.symbol)
		recv_amount = ""
		recv_symbol = ""
	else:
		sent_amount = ""
		sent_symbol = ""
		recv_amount = str(op.amount)
		recv_symbol = str(op.symbol)

	return [
		utils.format_date(op.date), # Date
		sent_amount,                # Sent Amount
		sent_symbol,                # Sent Currency
		recv_amount,                # Received Amount
		recv_symbol,                # Received Currency
		"",                         # Fee Amount
		"",                         # Fee Currency
		"",                         # Net Worth Amount
		"",                         # Net Worth Currency
		utils.koinly_tag(op.type),  # Label
		"",                         # Description
		"",                         # TxHash
	]


def order_by_date(lst: list[Transaction]) -> list[Transaction]:
	return sorted(lst, key=lambda t: t.date)


def write_output_file(output_file: str, contents: csv_type) -> None:
	with open(output_file, "w", encoding="utf-8", newline="\n") as file:
		writer = csv.writer(file)
		writer.writerows(contents)
