from collections import defaultdict
from typing import cast

from ..queries import is_trade
from ..types import Transaction, TransactionGroups, Trade, NonTrade


def group_similar_by_summary(lst: list[Transaction]) -> TransactionGroups:
	"""
	Group transactions that have the same summary
	"""
	groups: TransactionGroups = defaultdict(list)
	for t in lst:
		idx = get_group_index(t)
		groups[idx].append(t)
	return groups


def get_group_index(t: Transaction) -> str:
	if is_trade(t):
		return cast(Trade, t).summary
	else:
		t = cast(NonTrade, t)
		return f"{t.operation.summary}+{t.operation.symbol}"
