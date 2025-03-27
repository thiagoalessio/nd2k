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


Transaction = Trade | NonTrade
TransactionGroups = defaultdict[str, list[Transaction]]


@dataclass
class PartialTrade:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation | None = None
	quote_asset:  Operation | None = None
	trading_fee:  Operation | None = None

	def complete(self) -> Trade:
		return Trade(**vars(self))
