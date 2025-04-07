from typing import cast
from ..types import CSV
from ..transaction import Transaction
from ..operation import Operation
from ..nontrade import NonTrade
from ..trade import Trade, PartialTrade
from ..swap import Swap, PartialSwap
from ..exchange import Exchange, PartialExchange


def parse_successful_rows(rows: CSV) -> list[Operation]:
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


def build_nontrades(ops: list[Operation]) -> list[NonTrade]:
	return [NonTrade(operation=op) for op in ops]


def build_swaps(ops: list[Operation]) -> list[Swap]:
	swaps   = []
	partial = None

	for op in ops:
		if not partial:
			partial = PartialSwap(op)
			continue
		swaps.append(partial.complete(op))
		partial = None

	return swaps


def build_exchanges(ops: list[Operation]) -> list[Exchange]:
	exchanges = []
	partial   = None

	for op in ops:
		if not partial:
			partial = PartialExchange(op)
			continue
		if op.is_exchange_fee():
			partial.trading_fee = op
		else:
			partial.quote_asset = op
		if partial.is_completed():
			exchanges.append(partial.complete())
			partial = None

	return exchanges


def build_trades(ops: list[Operation]) -> list[Trade]:
	trades = []
	partials: list[PartialTrade] = []

	for op in ops:
		tr = create_or_update_trade(op, partials)
		if tr.is_completed():
			trades.append(tr.complete())
			partials.remove(tr)

	if len(partials):
		organize_rows_failed(partials)

	return trades


def organize_rows(rows: CSV) -> list[Transaction]:
	"""
	Each row in the NovaDAX CSV is an Operation,
	but Koinly expects each row to be a Transaction.
	Transactions can consist of one or more operations:
	- Trades have 3 operations: base asset, quote asset and trading fee.
	- Non-Trades, such as deposits and withdraws, have a single operation.
	"""
	operations  = parse_successful_rows(rows)
	categorized = categorize_by_type(operations)
	swaps       = build_swaps(categorized["swaps"])
	trades      = build_trades(categorized["trades"])
	exchanges   = build_exchanges(categorized["exchanges"])
	nontrades   = build_nontrades(categorized["nontrades"])

	return cast(list[Transaction], trades + swaps + exchanges + nontrades)


def create_or_update_trade(op: Operation, lst: list[PartialTrade]) -> PartialTrade:
	"""
	Attempts to fit operation into an existing partial trade.
	If it doesn't find any match, create a new partial trade.
	"""
	for pt in lst:
		if pt.fits_as_base_asset(op):
			pt.base_asset = op
			return pt

		if pt.fits_as_quote_asset(op):
			pt.quote_asset = op
			return pt

		if pt.fits_as_trading_fee(op):
			pt.trading_fee = op
			return pt

	pt = PartialTrade.from_operation(op)
	lst.append(pt)
	return pt


def organize_rows_failed(lst: list[PartialTrade]) -> None:
	"""
	If by the end of "organize_rows" we still have partial trades,
	something is wrong and the program shouldn't proceed.
	"""
	error_msg = "Error! The script went through all rows in the NovaDAX CSV "
	error_msg+= "and could not complete the following trades:\n\n"

	for pt in lst:
		base  = print_operation(pt.base_asset)
		quote = print_operation(pt.quote_asset)
		fee   = print_operation(pt.trading_fee)

		error_msg+= f"base asset:  {base}\n"
		error_msg+= f"quote asset: {quote}\n"
		error_msg+= f"trading fee: {fee}\n\n"

	error_msg+= "The input file may be faulty, "
	error_msg+= "or the script misinterpreted its contents.\n"
	error_msg+= "If you are sure the input file is correct, please open an "
	error_msg+= "issue at https://github.com/thiagoalessio/nd2k/issues/new "
	error_msg+= "and attach the file that caused this error.\n"
	print(error_msg)
	exit(1)


def print_operation(op: Operation | None) -> str:
	if not op:
		return "<empty>"
	return " | ".join([str(v) for k,v in op.__dict__.items() if k != "type"])
