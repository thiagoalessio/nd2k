import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, cast
from .transaction import Transaction
from .operation import Operation
from .types import group_by_timestamp


class TradingPair(NamedTuple):
	"""
	In a trading pair like BTC/EUR:
	- Base asset (BTC): The asset being bought or sold.
	- Quote asset (EUR): The asset used to price the base asset.
	"""
	base:  str
	quote: str

	@classmethod
	def from_string(cls, string: str) -> "TradingPair":
		match = re.search(r"\(([^\/]+)\/([^\)]+)", string)
		if match:
			return cls(*match.groups())
		raise ValueError(f"No trading pair found in \"{string}\"")


@dataclass
class TradeTraits:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation | None = None
	quote_asset:  Operation | None = None
	trading_fee:  Operation | None = None


	def fits_as_base_asset(self, op: Operation) -> bool:
		return (
			not self.base_asset
			and op.summary == self.summary
			and op.symbol  == self.trading_pair.base)


	def fits_as_quote_asset(self, op: Operation) -> bool:
		return (
			not self.quote_asset
			and op.summary == self.summary
			and op.symbol  == self.trading_pair.quote)


	def fits_as_trading_fee(self, op: Operation) -> bool:
		if self.trading_fee or not op.is_trading_fee():
			return False

		if self.is_a_purchase():
			return op.symbol == self.trading_pair.base

		if self.is_a_sale():
			return op.symbol == self.trading_pair.quote

		raise ValueError("Malformed Trade")


	def is_a_purchase(self) -> bool:
		return self._any_asset.type.name == "BUY"


	def is_a_sale(self) -> bool:
		return self._any_asset.type.name == "SELL"


	@property
	def _any_asset(self) -> Operation:
		any_asset = self.base_asset or self.quote_asset
		if any_asset:
			return any_asset
		raise ValueError("Empty Trade")	


@dataclass
class Trade(Transaction, TradeTraits):
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation
	quote_asset:  Operation
	trading_fee:  Operation


	@property
	def date(self) -> datetime:
		return self.base_asset.date


	@property
	def group_index(self) -> str:
		return "".join([str(self.date), self.summary])


	def format(self) -> list[str]:
		sent = self.quote_asset if self.is_a_purchase() else self.base_asset
		recv = self.base_asset  if self.is_a_purchase() else self.quote_asset

		return [
			self.formatted_date,          # Date
			f"{sent.amount}",             # Sent Amount
			f"{sent.symbol}",             # Sent Currency
			f"{recv.amount}",             # Received Amount
			f"{recv.symbol}",             # Received Currency
			f"{self.trading_fee.amount}", # Fee Amount
			f"{self.trading_fee.symbol}", # Fee Currency
			"",                           # Net Worth Amount
			"",                           # Net Worth Currency
			"trade",                      # Label
			self.base_asset.summary,      # Description
			"",                           # TxHash
		]


class PartialTrade(TradeTraits):
	@classmethod
	def from_operation(cls, op: Operation) -> "PartialTrade":
		tr = cls(
			summary = op.summary,
			trading_pair = TradingPair.from_string(op.summary)
		)
		tr.base_asset  = op if tr.fits_as_base_asset(op)  else None
		tr.quote_asset = op if tr.fits_as_quote_asset(op) else None
		return tr


	def is_completed(self) -> bool:
		return all([self.base_asset, self.quote_asset, self.trading_fee])


	def complete(self) -> Trade:
		return Trade(**vars(self))


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

	groups = group_by_timestamp(cast(list[Transaction], trades)).values()
	return [combine(cast(list[Trade], g)) for g in groups]


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


def combine(lst: list[Trade]) -> Trade:
	pt = PartialTrade.from_operation(lst[0].base_asset)
	pt.quote_asset = lst[0].quote_asset
	pt.trading_fee = lst[0].trading_fee
	tr = pt.complete()

	tr.base_asset.amount  = Decimal(sum(i.base_asset.amount  for i in lst))
	tr.quote_asset.amount = Decimal(sum(i.quote_asset.amount for i in lst))
	tr.trading_fee.amount = Decimal(sum(i.trading_fee.amount for i in lst))

	return tr
