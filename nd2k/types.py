from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import NamedTuple


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


class TradingPair(NamedTuple):
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


@dataclass
class PartialTrade:
	summary:      str
	trading_pair: TradingPair
	base_asset:   Operation | None = None
	quote_asset:  Operation | None = None
	trading_fee:  Operation | None = None

	def complete(self) -> Trade:
		return Trade(**vars(self))
