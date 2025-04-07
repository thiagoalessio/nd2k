import re
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple
from .transaction import Transaction
from .operation import Operation


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
