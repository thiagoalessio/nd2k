from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import cast

from .transaction import Transaction, group_by_timestamp
from .operation import Operation


@dataclass
class Exchange(Transaction):
	base_asset:   Operation
	quote_asset:  Operation
	exchange_fee: Operation


	@property
	def date(self) -> datetime:
		return self.base_asset.date


	@property
	def group_index(self) -> str:
		return "".join([
			str(self.date),
			self.base_asset.symbol,
			self.quote_asset.symbol
		])


	def format(self) -> list[str]:
		return [
			self.formatted_date,           # Date
			f"{self.base_asset.amount}",   # Sent Amount
			f"{self.base_asset.symbol}",   # Sent Currency
			f"{self.quote_asset.amount}",  # Received Amount
			f"{self.quote_asset.symbol}",  # Received Currency
			f"{self.exchange_fee.amount}", # Fee Amount
			f"{self.exchange_fee.symbol}", # Fee Currency
			"",                            # Net Worth Amount
			"",                            # Net Worth Currency
			"exchange",                    # Label
			self.base_asset.summary,       # Description
			"",                            # TxHash
		]


class PartialExchange:
	base_asset:   Operation
	quote_asset:  Operation | None
	exchange_fee: Operation | None


	def __init__(self, base_asset: Operation):
		self.base_asset   = base_asset
		self.quote_asset  = None
		self.exchange_fee = None


	def is_completed(self) -> bool:
		return all([self.base_asset, self.quote_asset, self.exchange_fee])


	def complete(self) -> Exchange:
		return Exchange(**vars(self))


def build(ops: list[Operation]) -> list[Exchange]:
	exchanges = []
	partial   = None

	for op in ops:
		if not partial:
			partial = PartialExchange(op)
			continue

		if op.is_exchange_fee():
			partial.exchange_fee = op
		else:
			partial.quote_asset = op

		if partial.is_completed():
			exchanges.append(partial.complete())
			partial = None

	if partial:
		raise ValueError("Incomplete Exchange", partial)

	groups = group_by_timestamp(cast(list[Transaction], exchanges))
	return [combine(cast(list[Exchange], g)) for g in groups.values()]


def combine(lst: list[Exchange]) -> Exchange:
	base  = lst[0].base_asset
	quote = lst[0].quote_asset
	fee   = lst[0].exchange_fee

	base.amount  = Decimal(sum(i.base_asset.amount   for i in lst))
	quote.amount = Decimal(sum(i.quote_asset.amount  for i in lst))
	fee.amount   = Decimal(sum(i.exchange_fee.amount for i in lst))

	return Exchange(base_asset=base, quote_asset=quote, exchange_fee=fee)
