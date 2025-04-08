import re
import unicodedata
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


	@classmethod
	def from_csv_row(cls, row: list[str]) -> "Operation":
		summary = unicodedata.normalize('NFC', row[1])
		return cls(
			date    = Operation.parse_date(row[0]),
			type    = OperationType(summary.split("(")[0]),
			summary = summary,
			symbol  = row[2],
			amount  = Operation.parse_amount(row[3]),
			status  = row[4],
		)


	@staticmethod
	def parse_date(data: str) -> datetime:
		return datetime.strptime(data, "%d/%m/%Y %H:%M:%S")


	@staticmethod
	def parse_amount(data: str) -> Decimal:
		pattern = r"^\D*([,\d]+)"
		matches = re.search(pattern, data)

		if not matches:
			raise ValueError(f"No numeric values found in \"{data}\"")

		parts = matches.group(1).split(",")
		last_part = parts.pop()

		# number has no commas, no decimals
		if not len(parts):
			return Decimal(last_part)

		# last comma acting as decimal separator
		int_part = "".join(parts)
		return Decimal(f"{int_part}.{last_part}")


	def is_successful(self) -> bool:
		return self.status == "Sucesso"


	def is_a_non_trade(self) -> bool:
		return self.type.name in [
			"CRYPTO_DEPOSIT",
			"FIAT_DEPOSIT",
			"CRYPTO_WITHDRAW",
			"FIAT_WITHDRAW",
			"WITHDRAW_FEE",
			"REDEEMED_BONUS",
		]


	def is_a_swap(self) -> bool:
		return self.type.name == "SWAP"


	def is_an_exchange(self) -> bool:
		return self.type.name == "EXCHANGE"


	def is_exchange_fee(self) -> bool:
		return self.type.name == "EXCHANGE_FEE"


	def belongs_to_an_exchange(self) -> bool:
		return self.is_an_exchange() or self.is_exchange_fee()


	def belongs_to_trade(self) -> bool:
		return self.type.name in ["BUY", "SELL"] or self.is_trading_fee()

	def is_trading_fee(self) -> bool:
		return self.type.name == "TRADING_FEE"

	def is_sending_funds(self) -> bool:
		return "WITHDRAW" in self.type.name
