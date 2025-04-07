from abc import ABC, abstractmethod
from datetime import datetime


class Transaction(ABC):

	@property
	@abstractmethod
	def date(self) -> datetime:
		pass

	@property
	@abstractmethod
	def group_index(self) -> str:
		pass

	@abstractmethod
	def format(self) -> list[str]:
		pass

	@property
	def formatted_date(self) -> str:
		return self.date.strftime("%Y-%m-%d %H:%M:%S")
