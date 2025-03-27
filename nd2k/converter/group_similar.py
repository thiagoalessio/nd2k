from collections import defaultdict
from ..types import Transaction, TransactionGroups


def group_similar_by_timestamp(lst: list[Transaction]) -> TransactionGroups:
	"""
	Group transactions that have the same timestamp+summary
	"""
	groups: TransactionGroups = defaultdict(list)
	for t in lst:
		groups[str(t.date) + t.summary].append(t)
	return groups
