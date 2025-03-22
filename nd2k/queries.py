from typing import cast
from .types import Operation, Trade


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

	if not tr.operations.base_asset and not tr.operations.quote_asset:
		raise ValueError("Empty Trade")

	any_asset = tr.operations.base_asset or tr.operations.quote_asset
	any_asset = cast(Operation, any_asset)

	if any_asset.type.name == "BUY":
		return op.symbol == tr.trading_pair.base

	if any_asset.type.name == "SELL":
		return op.symbol == tr.trading_pair.quote

	raise ValueError("Malformed Trade")


def is_trading_fee(op: Operation) -> bool:
	return op.type.name == "TRADING_FEE"
