import unicodedata
import re
from datetime import datetime
from decimal import Decimal
from ..types import (
	CSV,
	Transaction,
	Trade,
	NonTrade,
	PartialTrade,
	Operation,
	OperationType,
)
from ..utils import parse_trading_pair
from .. import queries as q


def organize_rows(rows: CSV) -> list[Transaction]:
	"""
	Each row in the NovaDAX CSV is an Operation,
	but Koinly expects each row to be a Transaction.
	Transactions can consist of one or more operations:
	- Trades have 3 operations: base asset, quote asset and trading fee.
	- Non-Trades, such as deposits and withdraws, have a single operation.
	"""
	trades: list[Trade] = []
	non_trades: list[NonTrade] = []
	partial_trades: list[PartialTrade] = []

	for row in rows:
		op = create_operation(row)
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
		organize_rows_failed(partial_trades)

	return trades + non_trades


def create_or_update_trade(op: Operation, lst: list[PartialTrade]) -> PartialTrade:
	"""
	Attempts to fit operation into an existing partial trade.
	If it doesn't find any match, create a new partial trade.
	"""
	for pt in lst:
		if q.fits_as_base_asset(op, pt):
			pt.base_asset = op
			return pt

		if q.fits_as_quote_asset(op, pt):
			pt.quote_asset = op
			return pt

		if q.fits_as_trading_fee(op, pt):
			pt.trading_fee = op
			return pt

	pt = create_partial_trade(op)
	lst.append(pt)
	return pt


def organize_rows_failed(lst: list[PartialTrade]) -> None:
	"""
	If by the end of "organize_rows" we still have partial trades,
	something is wrong and the program shouldn't proceed.
	"""
	error_msg = "Error! The script went through all rows in the NovaDAX CSV "
	error_msg+= "and could not complete the following trades:\n\n"
	error_msg+= "\n".join(str(pt) for pt in lst)
	error_msg+= "\nThe input file may be faulty, "
	error_msg+= "or the script misinterpreted its contents.\n"
	error_msg+= "If you are sure the input file is correct, please open an "
	error_msg+= "issue at https://github.com/thiagoalessio/nd2k/issues/new "
	error_msg+= "and attach the file that caused this error.\n"
	print(error_msg)
	exit(1)


def create_operation(csv_line: list[str]) -> Operation:
	summary = unicodedata.normalize('NFC', csv_line[1])
	return Operation(
		date    = parse_date(csv_line[0]),
		type    = OperationType(summary.split("(")[0]),
		summary = summary,
		symbol  = csv_line[2],
		amount  = parse_amount(csv_line[3]),
		status  = csv_line[4],
	)


def create_partial_trade(op: Operation) -> PartialTrade:
	tr = PartialTrade(
		summary      = op.summary,
		trading_pair = parse_trading_pair(op.summary))
	tr.base_asset  = op if q.fits_as_base_asset(op, tr)  else None
	tr.quote_asset = op if q.fits_as_quote_asset(op, tr) else None
	return tr


def parse_date(data: str) -> datetime:
	return datetime.strptime(data, "%d/%m/%Y %H:%M:%S")


def parse_amount(data: str) -> Decimal:
	pattern = r"^\D*([,\d]+)"
	matches = re.search(pattern, data)

	if not matches:
		raise ValueError(f"No numeric values found in \"{data}\"")

	parts = matches.group(1).split(",")
	last_part = parts.pop()

	# number has no commas, no decimals
	if not len(parts):
		return Decimal(last_part)

	# last comma acting as decimal separator
	int_part = "".join(parts)
	return Decimal(f"{int_part}.{last_part}")
