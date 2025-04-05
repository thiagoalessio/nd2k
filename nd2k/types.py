from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NamedTuple


CSV = list[list[str]]


class OperationType(Enum):
	CRYPTO_DEPOSIT  = "Depósito de criptomoedas"
	FIAT_DEPOSIT    = "Depósito em Reais"
	CRYPTO_WITHDRAW = "Saque de criptomoedas"
	FIAT_WITHDRAW   = "Saque em Reais"
	WITHDRAW_FEE    = "Taxa de saque de criptomoedas"
	REDEEMED_BONUS  = "Redeemed Bonus"
	BUY             = "Compra"
	SELL            = "Venda"
	TRADING_FEE     = "Taxa de transação"
	SWAP            = "Troca"


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


@dataclass
class Operation:
	date:    datetime
	type:    OperationType
	summary: str
	symbol:  str
	amount:  Decimal
	status:  str


@dataclass
class NonTrade: # a.k.a. "Simple Transaction"
	operation: Operation

	@property
	def date(self) -> datetime:
		return self.operation.date

	@property
	def summary(self) -> str:
		return self.operation.summary


class TradingPair(NamedTuple):
	"""
	In a trading pair like BTC/EUR:
	- Base asset (BTC): The asset being bought or sold.
	- Quote asset (EUR): The asset used to price the base asset.
	"""
	base:  str
	quote: str


@dataclass
class Trade:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation
	quote_asset:  Operation
	trading_fee:  Operation

	@property
	def date(self) -> datetime:
		return self.base_asset.date

	@property
	def type(self) -> OperationType:
		return self.base_asset.type


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
		self.asset_b = None

	def complete(self, asset_b: Operation) -> Swap:
		return Swap(asset_a=self.asset_a, asset_b=asset_b)


Transaction = Trade | NonTrade | Swap
TransactionGroups = defaultdict[str, list[Transaction]]


@dataclass
class PartialTrade:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation | None = None
	quote_asset:  Operation | None = None
	trading_fee:  Operation | None = None

	@property
	def type(self) -> OperationType:
		return self._any_asset.type

	@property
	def _any_asset(self) -> Operation:
		any_asset = self.base_asset or self.quote_asset
		if any_asset:
			return any_asset
		raise ValueError("Empty Trade")

	def complete(self) -> Trade:
		return Trade(**vars(self))
