from dataclasses import dataclass
from datetime import datetime
from .operation import Operation


@dataclass
class Swap:
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


class PartialSwap:
	def __init__(self, asset_a: Operation):
		self.asset_a = asset_a

	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)
