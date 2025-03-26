from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, Optional, cast


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


class Transaction(ABC):
	@property
	@abstractmethod
	def date(self) -> datetime:
		pass


@dataclass
class NonTrade(Transaction): # a.k.a. "Simple Transaction"
	operation: Operation

	@property
	def date(self) -> datetime:
		return self.operation.date


class TradingPair(NamedTuple):
	base:  str
	quote: str


@dataclass
class TradeOperations:
	base_asset:  Optional[Operation|None] = field(default_factory=lambda:None)
	quote_asset: Optional[Operation|None] = field(default_factory=lambda:None)
	trading_fee: Optional[Operation|None] = field(default_factory=lambda:None)


@dataclass
class Trade(Transaction):
	summary:      str
	operations:   TradeOperations
	trading_pair: TradingPair

	@property
	def date(self) -> datetime:
		return cast(Operation, self.operations.base_asset).date
