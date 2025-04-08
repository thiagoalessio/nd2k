from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import cast

from .transaction import Transaction, group_by_timestamp
from .operation import Operation


@dataclass
class NonTrade(Transaction): # a.k.a. "Simple Transaction"
	operation: Operation


	@property
	def date(self) -> datetime:
		return self.operation.date


	@property
	def group_index(self) -> str:
		return "".join([
			str(self.date),
			self.operation.summary,
			self.operation.symbol
		])


	def format(self) -> list[str]:
		sent = self.operation if self.operation.is_sending_funds() else None
		recv = None if sent else self.operation

		return [
			self.formatted_date,              # Date
			f"{sent.amount if sent else ''}", # Sent Amount
			f"{sent.symbol if sent else ''}", # Sent Currency
			f"{recv.amount if recv else ''}", # Received Amount
			f"{recv.symbol if recv else ''}", # Received Currency
			"",                               # Fee Amount
			"",                               # Fee Currency
			"",                               # Net Worth Amount
			"",                               # Net Worth Currency
			self.koinly_tag(),                # Label
			self.operation.summary,           # Description
			"",                               # TxHash
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


def build(ops: list[Operation]) -> list[NonTrade]:
	nontrades = [NonTrade(operation=op) for op in ops]
	groups = group_by_timestamp(cast(list[Transaction], nontrades))
	return [combine(cast(list[NonTrade], g)) for g in groups.values()]


def combine(lst: list[NonTrade]) -> NonTrade:
	op = lst[0].operation
	op.amount = Decimal(sum(i.operation.amount for i in lst))
	return NonTrade(operation=op)
