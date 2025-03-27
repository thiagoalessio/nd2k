import re
from .types import TradingPair, Transaction


def output_file(path: str) -> str:
	name = re.sub(r"\.csv$", "", path)
	return f"{name}_koinly_universal.csv"


def parse_trading_pair(data: str) -> TradingPair:
	match = re.search(r"\(([^\/]+)\/([^\)]+)", data)
	if match:
		return TradingPair(*match.groups())
	raise ValueError(f"No trading pair found in \"{data}\"")


def order_by_date(lst: list[Transaction]) -> list[Transaction]:
	return sorted(lst, key=lambda t: t.date)
