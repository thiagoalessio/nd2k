from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .operation import OperationType, Operation
from .nontrade import NonTrade
from .trade import Trade


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


@dataclass
class Swap:
	asset_a: Operation
	asset_b: Operation

	@property
	def date(self) -> datetime:
		return self.asset_a.date

	@property
	def summary(self) -> str:
		return "".join([
			self.asset_a.summary,
			self.asset_a.symbol,
			"/",
			self.asset_b.symbol
		])


class PartialSwap:
	def __init__(self, asset_a: Operation):
		self.asset_a = asset_a

	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)


@dataclass
class Exchange:
	base_asset:  Operation
	quote_asset: Operation
	trading_fee: Operation

	@property
	def date(self) -> datetime:
		return self.base_asset.date

	@property
	def type(self) -> OperationType:
		return self.base_asset.type


class PartialExchange:
	quote_asset: Operation | None
	trading_fee: Operation | None

	def __init__(self, base_asset: Operation):
		self.base_asset  = base_asset
		self.quote_asset = None
		self.trading_fee = None

	def complete(self) -> Exchange:
		return Exchange(**vars(self))


Transaction = Trade | NonTrade | Swap | Exchange
TransactionGroups = defaultdict[str, list[Transaction]]
