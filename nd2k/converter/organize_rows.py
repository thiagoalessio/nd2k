import re
from typing import cast
from ..types import CSV
from ..transaction import Transaction
from ..operation import Operation
from ..nontrade import NonTrade
from ..trade import Trade, PartialTrade, TradingPair
from ..swap import Swap, PartialSwap
from ..exchange import Exchange, PartialExchange
from .. import queries as q


def organize_rows(rows: CSV) -> list[Transaction]:
	"""
	Each row in the NovaDAX CSV is an Operation,
	but Koinly expects each row to be a Transaction.
	Transactions can consist of one or more operations:
	- Trades have 3 operations: base asset, quote asset and trading fee.
	- Non-Trades, such as deposits and withdraws, have a single operation.
	"""
	swaps: list[Swap] = []
	trades: list[Trade] = []
	exchanges: list[Exchange] = []
	non_trades: list[NonTrade] = []
	partial_trades: list[PartialTrade] = []
	partial_swap = None
	partial_exchange = None

	for row in rows:
		op = Operation.from_csv_row(row)
		if not op.is_successful():
			continue

		if q.is_a_non_trade(op):
			non_trades.append(NonTrade(operation=op))
			continue

		if q.is_a_swap(op):
			if partial_swap:
				swaps.append(partial_swap.complete(op))
				partial_swap = None
				continue

			partial_swap = PartialSwap(op)
			continue

		if q.belongs_to_an_exchange(op):
			if partial_exchange:
				if q.is_exchange_fee(op):
					partial_exchange.trading_fee = op
				else:
					partial_exchange.quote_asset = op

				if q.is_completed(partial_exchange):
					exchanges.append(partial_exchange.complete())
					partial_exchange = None
					continue
				continue

			partial_exchange = PartialExchange(op)
			continue

		if q.belongs_to_trade(op):
			tr = create_or_update_trade(op, partial_trades)

			if q.is_completed(tr):
				trades.append(tr.complete())
				partial_trades.remove(tr)

	if len(partial_trades):
		organize_rows_failed(partial_trades)

	return cast(list[Transaction], trades + swaps + exchanges + non_trades)


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


def create_partial_trade(op: Operation) -> PartialTrade:
	tr = PartialTrade(
		summary      = op.summary,
		trading_pair = parse_trading_pair(op.summary))
	tr.base_asset  = op if q.fits_as_base_asset(op, tr)  else None
	tr.quote_asset = op if q.fits_as_quote_asset(op, tr) else None
	return tr


def parse_trading_pair(data: str) -> TradingPair:
	match = re.search(r"\(([^\/]+)\/([^\)]+)", data)
	if match:
		return TradingPair(*match.groups())
	raise ValueError(f"No trading pair found in \"{data}\"")


def print_operation(op: Operation | None) -> str:
	if not op:
		return "<empty>"
	return " | ".join([str(v) for k,v in op.__dict__.items() if k != "type"])
