import re
import sys
import os
import csv

from . import __version__, types, converter, formatter
from .types import Transaction


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
	transactions = converter.organize_rows(csv_rows)
	combined     = converter.combine_by_timestamp(transactions)
	ordered      = order_by_date(combined)
	formatted    = formatter.universal(ordered)

	output_file = re.sub(r"\.csv$", "", input_file) + "_koinly_universal.csv"
	write(output_file, formatted)


def read(path: str) -> types.CSV:
	"""
	The NovaDAX CSV file must be read in reverse order to
	correctly match trades with their corresponding fees.
	"""
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return list(reversed(list(csv.reader(f))[1:]))


def order_by_date(lst: list[Transaction]) -> list[Transaction]:
	return sorted(lst, key=lambda t: t.date)


def write(path: str, contents: types.CSV) -> None:
	with open(path, "w", encoding="utf-8", newline="\n") as f:
		writer = csv.writer(f)
		writer.writerows(contents)
