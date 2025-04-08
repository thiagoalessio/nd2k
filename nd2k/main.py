import re
import sys
import os
import csv

from collections import defaultdict
from typing import cast, Any
from pprint import pformat

from . import __version__, swap, trade, exchange, nontrade
from .transaction import Transaction
from .operation import Operation


CSV = list[list[str]]


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
	ordered      = order_by_date(transactions)
	formatted    = koinly_universal_format(ordered)

	output_file = re.sub(r"\.csv$", "", input_file) + "_koinly_universal.csv"
	write(output_file, formatted)


def read(path: str) -> CSV:
	"""
	The NovaDAX CSV file must be read in reverse order to
	correctly match trades with their corresponding fees.
	"""
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return list(reversed(list(csv.reader(f))[1:]))


def organize_rows(rows: CSV) -> list[Transaction]:
	operations  = parse_successful_rows(rows)
	categorized = categorize_by_type(operations)

	try:
		swaps     = swap.build(categorized["swaps"])
		trades    = trade.build(categorized["trades"])
		exchanges = exchange.build(categorized["exchanges"])
		nontrades = nontrade.build(categorized["nontrades"])
	except ValueError as e:
		organize_rows_failed(e.args)

	return cast(list[Transaction], trades + swaps + exchanges + nontrades)


def parse_successful_rows(rows: CSV) -> list[Operation]:
	operations = []
	for row in rows:
		op = Operation.from_csv_row(row)
		if op.is_successful():
			operations.append(op)
	return operations


def categorize_by_type(ops: list[Operation]) -> dict[str, list[Operation]]:
	categorized = defaultdict(list)
	conditions  = {
		"swaps":     "is_a_swap",
		"trades":    "belongs_to_trade",
		"exchanges": "belongs_to_an_exchange",
		"nontrades": "is_a_non_trade"
	}
	for op in ops:
		for category, condition in conditions.items():
			if getattr(op, condition)():
				categorized[category].append(op)
	return categorized


def organize_rows_failed(leftovers: Any) -> None:
	error_msg = "Error! The script went through all rows in the NovaDAX CSV "
	error_msg+= "and could not find a match for the following operations:\n\n"

	error_msg+= pformat(leftovers, indent=2, width=80)

	error_msg+= "\n\nThe input file may be faulty, "
	error_msg+= "or the script misinterpreted its contents.\n"
	error_msg+= "If you are sure the input file is correct, please open an "
	error_msg+= "issue at https://github.com/thiagoalessio/nd2k/issues/new "
	error_msg+= "and attach the file that caused this error.\n"
	print(error_msg)
	exit(1)


def order_by_date(lst: list[Transaction]) -> list[Transaction]:
	return sorted(lst, key=lambda t: t.date)


def koinly_universal_format(transactions: list[Transaction]) -> CSV:
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


def write(path: str, contents: CSV) -> None:
	with open(path, "w", encoding="utf-8", newline="\n") as f:
		writer = csv.writer(f)
		writer.writerows(contents)
