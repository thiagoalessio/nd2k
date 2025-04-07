import re
import sys
import os
import csv

from collections import defaultdict
from typing import cast
from . import __version__, types, converter, swap, trade, exchange, nontrade
from .transaction import Transaction
from .operation import Operation


def main() -> None:
	if len(sys.argv) != 2:
		print("Usage: nd2k <novadax-csv>")
		exit(1)

	if sys.argv[1] in ["-v", "--version"]:
		print(__version__)
		exit(0)

	input_file = sys.argv[1]

	if not os.path.exists(input_file):
		print(f"Error: No such file: {input_file}")
		exit(1)

	csv_rows     = read(input_file)
	transactions = organize_rows(csv_rows)
	grouped      = group_by_timestamp(transactions)
	combined     = converter.combine_groups(grouped)
	ordered      = order_by_date(combined)
	formatted    = format(ordered)

	output_file = re.sub(r"\.csv$", "", input_file) + "_koinly_universal.csv"
	write(output_file, formatted)


def read(path: str) -> types.CSV:
	"""
	The NovaDAX CSV file must be read in reverse order to
	correctly match trades with their corresponding fees.
	"""
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return list(reversed(list(csv.reader(f))[1:]))


def organize_rows(rows: types.CSV) -> list[Transaction]:
	operations  = parse_successful_rows(rows)
	categorized = categorize_by_type(operations)
	swaps       = swap.build_swaps(categorized["swaps"])
	trades      = trade.build_trades(categorized["trades"])
	exchanges   = exchange.build_exchanges(categorized["exchanges"])
	nontrades   = nontrade.build_nontrades(categorized["nontrades"])

	return cast(list[Transaction], trades + swaps + exchanges + nontrades)


def parse_successful_rows(rows: types.CSV) -> list[Operation]:
	operations = []
	for row in rows:
		op = Operation.from_csv_row(row)
		if op.is_successful():
			operations.append(op)
	return operations


def categorize_by_type(ops: list[Operation]) -> dict[str, list[Operation]]:
	return {
		"swaps":     [op for op in ops if op.is_a_swap()],
		"trades":    [op for op in ops if op.belongs_to_trade()],
		"exchanges": [op for op in ops if op.belongs_to_an_exchange()],
		"nontrades": [op for op in ops if op.is_a_non_trade()],
	}


def group_by_timestamp(lst: list[Transaction]) -> types.TransactionGroups:
	groups: types.TransactionGroups = defaultdict(list)
	for t in lst:
		groups[t.group_index].append(t)
	return groups


def order_by_date(lst: list[Transaction]) -> list[Transaction]:
	return sorted(lst, key=lambda t: t.date)


def format(transactions: list[Transaction]) -> types.CSV:
	rows = []
	rows.append([ # headers
		"Date",
		"Sent Amount",
		"Sent Currency",
		"Received Amount",
		"Received Currency",
		"Fee Amount",
		"Fee Currency",
		"Net Worth Amount",
		"Net Worth Currency",
		"Label",
		"Description",
	])
	for t in transactions:
		rows.append(t.format())
	return rows


def write(path: str, contents: types.CSV) -> None:
	with open(path, "w", encoding="utf-8", newline="\n") as f:
		writer = csv.writer(f)
		writer.writerows(contents)
