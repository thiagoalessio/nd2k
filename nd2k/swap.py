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
	def group_index(self) -> str:
		return "".join([
			str(self.date),
			self.asset_a.summary,
			self.asset_a.symbol,
			self.asset_b.symbol
		])


	def format(self) -> list[str]:
		return [
			self.formatted_date,      # Date
			f"{self.asset_a.amount}", # Sent Amount
			f"{self.asset_a.symbol}", # Sent Currency
			f"{self.asset_b.amount}", # Received Amount
			f"{self.asset_b.symbol}", # Received Currency
			"",                       # Fee Amount
			"",                       # Fee Currency
			"",                       # Net Worth Amount
			"",                       # Net Worth Currency
			"swap",                   # Label
			self.asset_a.summary,     # Description
			"",                       # TxHash
		]


class PartialSwap:
	def __init__(self, asset_a: Operation):
		self.asset_a = asset_a


	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)


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
