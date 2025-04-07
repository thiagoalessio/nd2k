from collections import defaultdict
from enum import Enum
from .nontrade import NonTrade
from .trade import Trade
from .swap import Swap
from .exchange import Exchange


CSV = list[list[str]]


class KoinlyTag(Enum):
	BUY             = "trade"
	SELL            = "trade"
	TRADING_FEE     = "fee"


Transaction = Trade | NonTrade | Swap | Exchange
TransactionGroups = defaultdict[str, list[Transaction]]
