from dataclasses import dataclass
from datetime import datetime
from .transaction import Transaction
from .operation import Operation


@dataclass
class Swap(Transaction):
	asset_a: Operation
	asset_b: Operation

	@property
	def date(self) -> datetime:
		return self.asset_a.date

	@property
	def summary(self) -> str:
		return "".join([
			self.asset_a.summary,
			self.asset_a.symbol,
			"/",
			self.asset_b.symbol
		])

	def format(self) -> list[str]:
		a = self.asset_a
		b = self.asset_b
		return [
			self.formatted_date, # Date
			f"{a.amount}",       # Sent Amount
			f"{a.symbol}",       # Sent Currency
			f"{b.amount}",       # Received Amount
			f"{b.symbol}",       # Received Currency
			"",                  # Fee Amount
			"",                  # Fee Currency
			"",                  # Net Worth Amount
			"",                  # Net Worth Currency
			"swap",              # Label
			a.summary,           # Description
			"",                  # TxHash
		]


class PartialSwap:
	def __init__(self, asset_a: Operation):
		self.asset_a = asset_a

	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)
