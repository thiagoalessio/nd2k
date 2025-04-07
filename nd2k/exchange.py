from dataclasses import dataclass
from datetime import datetime
from .transaction import Transaction
from .operation import Operation, OperationType


@dataclass
class Exchange(Transaction):
	base_asset:  Operation
	quote_asset: Operation
	trading_fee: Operation

	@property
	def date(self) -> datetime:
		return self.base_asset.date

	@property
	def type(self) -> OperationType:
		return self.base_asset.type

	def format(self) -> list[str]:
		return [
			format_date(self.base_asset.date), # Date
			f"{self.base_asset.amount}",       # Sent Amount
			f"{self.base_asset.symbol}",       # Sent Currency
			f"{self.quote_asset.amount}",      # Received Amount
			f"{self.quote_asset.symbol}",      # Received Currency
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
			"EXCHANGE": "exchange",
			"EXCHANGE_FEE": "fee",
		}[self.base_asset.type.name]


class PartialExchange:
	quote_asset: Operation | None
	trading_fee: Operation | None

	def __init__(self, base_asset: Operation):
		self.base_asset  = base_asset
		self.quote_asset = None
		self.trading_fee = None

	def complete(self) -> Exchange:
		return Exchange(**vars(self))


def format_date(data: datetime) -> str:
	return data.strftime("%Y-%m-%d %H:%M:%S")
