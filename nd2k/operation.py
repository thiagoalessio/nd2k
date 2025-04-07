from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


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
	EXCHANGE        = "Convert"
	EXCHANGE_FEE    = "Taxa de Convert"

@dataclass
class Operation:
	date:    datetime
	type:    OperationType
	summary: str
	symbol:  str
	amount:  Decimal
	status:  str
