from dataclasses import dataclass
from datetime import datetime
from .operation import Operation


@dataclass
class NonTrade: # a.k.a. "Simple Transaction"
	operation: Operation

	@property
	def date(self) -> datetime:
		return self.operation.date

	@property
	def summary(self) -> str:
		return self.operation.summary

	def format(self) -> list[str]:
		op = self.operation

		if is_sending_funds(op):
			sent_amount = str(op.amount)
			sent_symbol = op.symbol
			recv_amount = ""
			recv_symbol = ""
		else:
			sent_amount = ""
			sent_symbol = ""
			recv_amount = str(op.amount)
			recv_symbol = op.symbol

		return [
			format_date(op.date), # Date
			sent_amount,          # Sent Amount
			sent_symbol,          # Sent Currency
			recv_amount,          # Received Amount
			recv_symbol,          # Received Currency
			"",                   # Fee Amount
			"",                   # Fee Currency
			"",                   # Net Worth Amount
			"",                   # Net Worth Currency
			self.koinly_tag(),    # Label
			op.summary,           # Description
			"",                   # TxHash
		]

	def koinly_tag(self) -> str:
		return {
			"CRYPTO_DEPOSIT":  "deposit",
			"FIAT_DEPOSIT":    "deposit",
			"CRYPTO_WITHDRAW": "withdraw",
			"FIAT_WITHDRAW":   "withdraw",
			"WITHDRAW_FEE":    "fee",
			"REDEEMED_BONUS":  "reward",
		}[self.operation.type.name]


def format_date(data: datetime) -> str:
	return data.strftime("%Y-%m-%d %H:%M:%S")


def is_sending_funds(op: Operation) -> bool:
	return "WITHDRAW" in op.type.name
