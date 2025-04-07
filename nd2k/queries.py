from .exchange import PartialExchange
from .trade import PartialTrade


def is_completed(tr: PartialTrade | PartialExchange) -> bool:
	return all([
		tr.base_asset,
		tr.quote_asset,
		tr.trading_fee])
