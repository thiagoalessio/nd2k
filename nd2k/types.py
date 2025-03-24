from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, Optional


class OperationType(Enum):
	DEPOSIT      = "Depósito de criptomoedas"
	WITHDRAW     = "Saque de criptomoedas"
	WITHDRAW_FEE = "Taxa de saque de criptomoedas"
	BUY          = "Compra"
	SELL         = "Venda"
	TRADING_FEE  = "Taxa de transação"


@dataclass
class Operation:
	date:    datetime
	type:    OperationType
	summary: str
	symbol:  str
	amount:  Decimal
	status:  str


class Transaction:
	pass


@dataclass
class NonTrade(Transaction): # a.k.a. "Simple Transaction"
	operation: Operation


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
