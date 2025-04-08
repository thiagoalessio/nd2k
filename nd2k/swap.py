from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import cast

from .transaction import Transaction, group_by_timestamp
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
	asset_a: Operation
	asset_b: Operation | None


	def __init__(self, asset_a: Operation):
		self.asset_a = asset_a
		self.asset_b = None


	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)


def build(ops: list[Operation]) -> list[Swap]:
	swaps   = []
	partial = None

	for op in ops:
		if not partial:
			partial = PartialSwap(op)
			continue

		swaps.append(partial.complete(op))
		partial = None

	if partial:
		raise ValueError("Incomplete Swap", partial)

	groups = group_by_timestamp(cast(list[Transaction], swaps)).values()
	return [combine(cast(list[Swap], g)) for g in groups]


def combine(lst: list[Swap]) -> Swap:
	a = lst[0].asset_a
	b = lst[0].asset_b
	a.amount = Decimal(sum(i.asset_a.amount for i in lst))
	b.amount = Decimal(sum(i.asset_b.amount for i in lst))
	return Swap(asset_a=a, asset_b=b)
