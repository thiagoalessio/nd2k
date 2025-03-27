from decimal import Decimal
from typing import cast

from ..queries import is_trade
from ..types import TransactionGroups, Transaction, Trade, NonTrade
from ..utils import parse_trading_pair


def combine_groups(groups: TransactionGroups) -> list[Transaction]:
	"""
	Combine all transactions of a group into
	a single transaction, summing up their amounts.
	"""
	combined: list[Transaction] = []

	for grp in groups.values():
		if all(is_trade(i) for i in grp):
			combined.append(combine_trades(cast(list[Trade], grp)))
		else:
			combined.append(combine_non_trades(cast(list[NonTrade], grp)))

	return combined


def combine_trades(lst: list[Trade]) -> Trade:
	base  = lst[0].base_asset
	quote = lst[0].quote_asset
	fee   = lst[0].trading_fee

	base.amount  = Decimal(sum(i.base_asset.amount  for i in lst))
	quote.amount = Decimal(sum(i.quote_asset.amount for i in lst))
	fee.amount   = Decimal(sum(i.trading_fee.amount for i in lst))

	trade = Trade(
		summary      = base.summary,
		trading_pair = parse_trading_pair(base.summary),
		base_asset   = base,
		quote_asset  = quote,
		trading_fee  = fee
	)
	return trade


def combine_non_trades(lst: list[NonTrade]) -> NonTrade:
	op = lst[0].operation
	op.amount = Decimal(sum(i.operation.amount for i in lst))
	return NonTrade(operation=op)
