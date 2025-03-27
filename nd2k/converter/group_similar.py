from collections import defaultdict
from typing import cast

from ..queries import is_trade
from ..types import Transaction, TransactionGroups, Trade, NonTrade


def group_similar_by_timestamp(lst: list[Transaction]) -> TransactionGroups:
	"""
	Group transactions that have the same timestamp+summary
	"""
	groups: TransactionGroups = defaultdict(list)
	for t in lst:
		idx = get_group_index(t)
		groups[idx].append(t)
	return groups


def get_group_index(t: Transaction) -> str:
	idx = str(t.date)
	if is_trade(t):
		idx += cast(Trade, t).summary
	else:
		idx += cast(NonTrade, t).operation.summary
	return idx
