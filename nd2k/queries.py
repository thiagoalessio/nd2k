from .types import Operation, Trade, TradeOperations


def is_successful(op: Operation) -> bool:
	return op.status == "Sucesso"


def is_part_of_a_trade(op: Operation) -> bool:
	return op.type.name in ["BUY", "SELL", "TRADING_FEE"]


def is_completed(tr: Trade) -> bool:
	return all([
		tr.operations.base_asset,
		tr.operations.quote_asset,
		tr.operations.trading_fee])


def fits_as_base_asset(op: Operation, tr: Trade) -> bool:
	return (
		not tr.operations.base_asset
		and op.summary == tr.summary
		and op.symbol  == tr.trading_pair.base)


def fits_as_quote_asset(op: Operation, tr: Trade) -> bool:
	return (
		not tr.operations.quote_asset
		and op.summary == tr.summary
		and op.symbol  == tr.trading_pair.quote)


def fits_as_trading_fee(op: Operation, tr: Trade) -> bool:
	if tr.operations.trading_fee:
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


def is_a_purchase(tr: Trade) -> bool:
	any_asset = get_any_asset(tr.operations)
	return any_asset.type.name == "BUY"


def is_a_sale(tr: Trade) -> bool:
	any_asset = get_any_asset(tr.operations)
	return any_asset.type.name == "SELL"


def get_any_asset(ops: TradeOperations) -> Operation:
	any_asset = ops.base_asset or ops.quote_asset
	if any_asset:
		return any_asset
	raise ValueError("Empty Trade")
