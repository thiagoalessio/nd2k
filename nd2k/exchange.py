from dataclasses import dataclass
from datetime import datetime
from .operation import Operation, OperationType


@dataclass
class Exchange:
	base_asset:  Operation
	quote_asset: Operation
	trading_fee: Operation

	@property
	def date(self) -> datetime:
		return self.base_asset.date

	@property
	def type(self) -> OperationType:
		return self.base_asset.type


class PartialExchange:
	quote_asset: Operation | None
	trading_fee: Operation | None

	def __init__(self, base_asset: Operation):
		self.base_asset  = base_asset
		self.quote_asset = None
		self.trading_fee = None

	def complete(self) -> Exchange:
		return Exchange(**vars(self))

