from collections import defaultdict
from .transaction import Transaction


CSV = list[list[str]]
TransactionGroups = defaultdict[str, list[Transaction]]


def group_by_timestamp(lst: list[Transaction]) -> TransactionGroups:
	groups: TransactionGroups = defaultdict(list)
	for t in lst:
		groups[t.group_index].append(t)
	return groups
