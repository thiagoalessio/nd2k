from collections import defaultdict
from decimal import Decimal
from typing import cast

from .organize_rows import create_partial_trade
from ..types import TransactionGroups, Transaction, Trade, NonTrade, Swap, Exchange


def combine_by_timestamp(lst: list[Transaction]) -> list[Transaction]:
	return combine_groups(group_by_timestamp(lst))


def group_by_timestamp(lst: list[Transaction]) -> TransactionGroups:
	"""
	Group transactions that have the same timestamp+summary
	"""
	groups: TransactionGroups = defaultdict(list)
	for t in lst:
		groups[generate_group_index(t)].append(t)
	return groups


def generate_group_index(t: Transaction) -> str:
	if isinstance(t, NonTrade):
		return str(t.date) + t.summary + t.operation.symbol

	if isinstance(t, Swap):
		return str(t.date) + t.summary + t.asset_a.symbol + t.asset_b.symbol

	if isinstance(t, Trade):
		return str(t.date) + t.summary

	if isinstance(t, Exchange):
		return str(t.date) + t.base_asset.symbol + t.quote_asset.symbol


def combine_groups(groups: TransactionGroups) -> list[Transaction]:
	"""
	Combine all transactions of a group into
	a single transaction, summing up their amounts.
	"""
	combined: list[Transaction] = []

	for grp in groups.values():
		if all(isinstance(i, Trade) for i in grp):
			combined.append(combine_trades(cast(list[Trade], grp)))
			continue

		if all(isinstance(i, Swap) for i in grp):
			combined.append(combine_swaps(cast(list[Swap], grp)))
			continue

		if all(isinstance(i, Exchange) for i in grp):
			combined.append(combine_exchanges(cast(list[Exchange], grp)))
			continue

		if all(isinstance(i, NonTrade) for i in grp):
			combined.append(combine_non_trades(cast(list[NonTrade], grp)))
			continue

	return combined


def combine_trades(lst: list[Trade]) -> Trade:
	pt = create_partial_trade(lst[0].base_asset)
	pt.quote_asset = lst[0].quote_asset
	pt.trading_fee = lst[0].trading_fee
	tr = pt.complete()

	tr.base_asset.amount  = Decimal(sum(i.base_asset.amount  for i in lst))
	tr.quote_asset.amount = Decimal(sum(i.quote_asset.amount for i in lst))
	tr.trading_fee.amount = Decimal(sum(i.trading_fee.amount for i in lst))

	return tr


def combine_swaps(lst: list[Swap]) -> Swap:
	a = lst[0].asset_a
	b = lst[0].asset_b
	a.amount = Decimal(sum(i.asset_a.amount for i in lst))
	b.amount = Decimal(sum(i.asset_b.amount for i in lst))
	return Swap(asset_a=a, asset_b=b)


def combine_non_trades(lst: list[NonTrade]) -> NonTrade:
	op = lst[0].operation
	op.amount = Decimal(sum(i.operation.amount for i in lst))
	return NonTrade(operation=op)


def combine_exchanges(lst: list[Exchange]) -> Exchange:
	return Exchange(
		base_asset  = lst[0].base_asset,
		quote_asset = lst[0].quote_asset,
		trading_fee = lst[0].trading_fee
	)
