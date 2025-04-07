from .exchange import PartialExchange
from .operation import Operation
from .trade import PartialTrade, Trade


def is_completed(tr: PartialTrade | PartialExchange) -> bool:
	return all([
		tr.base_asset,
		tr.quote_asset,
		tr.trading_fee])


def fits_as_base_asset(op: Operation, tr: PartialTrade) -> bool:
	return (
		not tr.base_asset
		and op.summary == tr.summary
		and op.symbol  == tr.trading_pair.base)


def fits_as_quote_asset(op: Operation, tr: PartialTrade) -> bool:
	return (
		not tr.quote_asset
		and op.summary == tr.summary
		and op.symbol  == tr.trading_pair.quote)


def fits_as_trading_fee(op: Operation, tr: PartialTrade) -> bool:
	if tr.trading_fee:
		return False

	if not op.is_trading_fee():
		return False

	if is_a_purchase(tr):
		return op.symbol == tr.trading_pair.base

	if is_a_sale(tr):
		return op.symbol == tr.trading_pair.quote

	raise ValueError("Malformed Trade")


def is_a_purchase(tr: Trade | PartialTrade) -> bool:
	return tr.type.name == "BUY"


def is_a_sale(tr: Trade | PartialTrade) -> bool:
	return tr.type.name == "SELL"
