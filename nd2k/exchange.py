from dataclasses import dataclass
from datetime import datetime
from .transaction import Transaction
from .operation import Operation


@dataclass
class Exchange(Transaction):
	base_asset:  Operation
	quote_asset: Operation
	trading_fee: Operation


	@property
	def date(self) -> datetime:
		return self.base_asset.date


	@property
	def group_index(self) -> str:
		return "".join([
			str(self.date),
			self.base_asset.symbol,
			self.quote_asset.symbol
		])


	def format(self) -> list[str]:
		return [
			self.formatted_date,          # Date
			f"{self.base_asset.amount}",  # Sent Amount
			f"{self.base_asset.symbol}",  # Sent Currency
			f"{self.quote_asset.amount}", # Received Amount
			f"{self.quote_asset.symbol}", # Received Currency
			f"{self.trading_fee.amount}", # Fee Amount
			f"{self.trading_fee.symbol}", # Fee Currency
			"",                           # Net Worth Amount
			"",                           # Net Worth Currency
			"exchange",                   # Label
			self.base_asset.summary,      # Description
			"",                           # TxHash
		]


class PartialExchange:
	quote_asset: Operation | None
	trading_fee: Operation | None

	def __init__(self, base_asset: Operation):
		self.base_asset  = base_asset
		self.quote_asset = None
		self.trading_fee = None


	def is_completed(self) -> bool:
		return all([self.base_asset, self.quote_asset, self.trading_fee])


	def complete(self) -> Exchange:
		return Exchange(**vars(self))
