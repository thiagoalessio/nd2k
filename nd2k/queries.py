from .types import Operation, PartialTrade, Transaction, Trade


def is_successful(op: Operation) -> bool:
	return op.status == "Sucesso"


def is_part_of_a_trade(op: Operation) -> bool:
	return op.type.name in ["BUY", "SELL", "TRADING_FEE"]


def is_completed(tr: PartialTrade) -> bool:
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

	if not is_trading_fee(op):
		return False

	if is_a_purchase(tr):
		return op.symbol == tr.trading_pair.base

	if is_a_sale(tr):
		return op.symbol == tr.trading_pair.quote

	raise ValueError("Malformed Trade")


def is_trading_fee(op: Operation) -> bool:
	return op.type.name == "TRADING_FEE"


def is_a_purchase(tr: PartialTrade) -> bool:
	any_asset = get_any_asset(tr)
	return any_asset.type.name == "BUY"


def is_a_sale(tr: PartialTrade) -> bool:
	any_asset = get_any_asset(tr)
	return any_asset.type.name == "SELL"


def get_any_asset(tr: PartialTrade) -> Operation:
	any_asset = tr.base_asset or tr.quote_asset
	if any_asset:
		return any_asset
	raise ValueError("Empty Trade")


def is_trade(t: Transaction) -> bool:
	return isinstance(t, Trade)
