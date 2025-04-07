from dataclasses import dataclass
from datetime import datetime
from .operation import Operation


@dataclass
class NonTrade: # a.k.a. "Simple Transaction"
	operation: Operation

	@property
	def date(self) -> datetime:
		return self.operation.date

	@property
	def summary(self) -> str:
		return self.operation.summary
