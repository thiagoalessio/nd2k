import sys
import os
import csv
from . import types, converter, utils, formatter


def main() -> None:
	if len(sys.argv) != 2:
		print("Usage: nd2k <novadax-csv>")
		exit(1)

	input_file = sys.argv[1]

	if not os.path.exists(input_file):
		print(f"Error: No such file: {input_file}")
		exit(1)

	csv_rows     = read(input_file)
	transactions = converter.organize_rows(csv_rows)
	grouped      = converter.group_similar_by_timestamp(transactions)
	combined     = converter.combine_groups(grouped)
	ordered      = utils.order_by_date(combined)
	formatted    = formatter.universal(ordered)

	output_file = utils.output_file(input_file, "koinly_universal")
	write(output_file, formatted)


def read(path: str) -> types.CSV:
	"""
	The NovaDAX CSV file must be read in reverse order to
	correctly match trades with their corresponding fees.
	"""
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return list(reversed(list(csv.reader(f))[1:]))


def write(path: str, contents: types.CSV) -> None:
	with open(path, "w", encoding="utf-8", newline="\n") as f:
		writer = csv.writer(f)
		writer.writerows(contents)
