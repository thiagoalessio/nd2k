from abc import ABC, abstractmethod
from collections import defaultdict
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


def group_by_timestamp(lst: list[Transaction]) -> dict[str, list[Transaction]]:
	groups = defaultdict(list)
	for t in lst:
		groups[t.group_index].append(t)
	return groups
