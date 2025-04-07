from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple
from .transaction import Transaction
from .operation import Operation, OperationType


class TradingPair(NamedTuple):
	"""
	In a trading pair like BTC/EUR:
	- Base asset (BTC): The asset being bought or sold.
	- Quote asset (EUR): The asset used to price the base asset.
	"""
	base:  str
	quote: str


@dataclass
class Trade(Transaction):
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation
	quote_asset:  Operation
	trading_fee:  Operation

	@property
	def date(self) -> datetime:
		return self.base_asset.date

	@property
	def type(self) -> OperationType:
		return self.base_asset.type

	def format(self) -> list[str]:
		if is_a_purchase(self):
			sent_amount = self.quote_asset.amount
			sent_symbol = self.quote_asset.symbol
			recv_amount = self.base_asset.amount
			recv_symbol = self.base_asset.symbol
		else:
			sent_amount = self.base_asset.amount
			sent_symbol = self.base_asset.symbol
			recv_amount = self.quote_asset.amount
			recv_symbol = self.quote_asset.symbol

		return [
			self.formatted_date,               # Date
			f"{sent_amount}",                  # Sent Amount
			f"{sent_symbol}",                  # Sent Currency
			f"{recv_amount}",                  # Received Amount
			f"{recv_symbol}",                  # Received Currency
			f"{self.trading_fee.amount}",      # Fee Amount
			f"{self.trading_fee.symbol}",      # Fee Currency
			"",                                # Net Worth Amount
			"",                                # Net Worth Currency
			self.koinly_tag(),                 # Label
			self.base_asset.summary,           # Description
			"",                                # TxHash
		]

	def koinly_tag(self) -> str:
		return {
			"BUY":         "trade",
			"SELL":        "trade",
			"TRADING_FEE": "fee",
		}[self.type.name]


@dataclass
class PartialTrade:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation | None = None
	quote_asset:  Operation | None = None
	trading_fee:  Operation | None = None

	@property
	def type(self) -> OperationType:
		return self._any_asset.type

	@property
	def _any_asset(self) -> Operation:
		any_asset = self.base_asset or self.quote_asset
		if any_asset:
			return any_asset
		raise ValueError("Empty Trade")

	def complete(self) -> Trade:
		return Trade(**vars(self))


def is_a_purchase(tr: Trade | PartialTrade) -> bool:
	return tr.type.name == "BUY"
