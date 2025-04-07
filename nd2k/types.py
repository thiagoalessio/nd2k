from collections import defaultdict
from .nontrade import NonTrade
from .trade import Trade
from .swap import Swap
from .exchange import Exchange


CSV = list[list[str]]
Transaction = Trade | NonTrade | Swap | Exchange
TransactionGroups = defaultdict[str, list[Transaction]]
