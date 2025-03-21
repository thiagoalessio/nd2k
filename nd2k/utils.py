import re

from datetime import datetime
from decimal import Decimal
from typing import cast
from .types import *


def output_filename(input_filename: str, suffix: str) -> str:
	name = re.sub(r"\.csv$", "", input_filename)
	return f"{name}_{suffix}.csv"


def parse_date(data: str) -> datetime:
	return datetime.strptime(data, "%d/%m/%Y %H:%M:%S")


def format_date(data: datetime) -> str:
	return data.strftime("%Y-%m-%d %H:%M:%S")


def parse_trading_pair(data: str) -> TradingPair:
	match = re.search(r"\(([^\/]+)\/([^\)]+)", data)
	if match:
		return TradingPair(*match.groups())
	raise ValueError(f"No trading pair found in \"{data}\"")


def format_trading_pair(data: TradingPair) -> str:
	return f"{data.base}/{data.quote}"


def parse_amount(data: str) -> Decimal:
	pattern = r"^\D*([,\d]+)"
	matches = re.search(pattern, data)

	if not matches:
		raise ValueError(f"No numeric values found in \"{data}\"")

	parts = matches.group(1).split(",")
	last_part = parts.pop()

	# number has no commas, no decimals
	if not len(parts):
		return Decimal(last_part)

	# last comma acting as decimal separator
	int_part = "".join(parts)
	return Decimal(f"{int_part}.{last_part}")


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

	if op.type.name != "TRADING_FEE":
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


def create_operation(csv_line: list[str]) -> Operation:
	return Operation(
		date    = parse_date(csv_line[0]),
		type    = OperationType(csv_line[1].split("(")[0]),
		summary = csv_line[1],
		symbol  = csv_line[2],
		amount  = parse_amount(csv_line[3]),
		status  = csv_line[4],
	)


def create_trade(op: Operation) -> Trade:
	tr = Trade(
		summary      = op.summary,
		operations   = TradeOperations(),
		trading_pair = parse_trading_pair(op.summary))

	tr.operations.base_asset  = op if fits_as_base_asset(op, tr)  else None
	tr.operations.quote_asset = op if fits_as_quote_asset(op, tr) else None
	return tr
