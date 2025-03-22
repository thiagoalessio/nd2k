import re

from datetime import datetime
from decimal import Decimal
from . import queries as q
from nd2k.types import (
	Operation,
	OperationType,
	Trade,
	TradeOperations,
	TradingPair,
)


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

	tr.operations.base_asset  = op if q.fits_as_base_asset(op, tr)  else None
	tr.operations.quote_asset = op if q.fits_as_quote_asset(op, tr) else None
	return tr
