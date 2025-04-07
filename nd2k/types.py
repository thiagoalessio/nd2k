from collections import defaultdict
from enum import Enum
from .nontrade import NonTrade
from .trade import Trade
from .swap import Swap
from .exchange import Exchange


CSV = list[list[str]]


class KoinlyTag(Enum):
	CRYPTO_DEPOSIT  = "deposit"
	FIAT_DEPOSIT    = "deposit"
	CRYPTO_WITHDRAW = "withdraw"
	FIAT_WITHDRAW   = "withdraw"
	WITHDRAW_FEE    = "fee"
	REDEEMED_BONUS  = "reward"
	BUY             = "trade"
	SELL            = "trade"
	TRADING_FEE     = "fee"
	SWAP            = "swap"
	EXCHANGE        = "exchange"
	EXCHANGE_FEE    = "fee"


Transaction = Trade | NonTrade | Swap | Exchange
TransactionGroups = defaultdict[str, list[Transaction]]
