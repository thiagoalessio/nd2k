from abc import ABC, abstractmethod
from datetime import datetime


class Transaction(ABC):

	@property
	@abstractmethod
	def date(self) -> datetime:
		pass

	@abstractmethod
	def format(self) -> list[str]:
		pass
