from typing import cast

from nd2k.exchange import Exchange, combine
from nd2k.transaction import Transaction, group_by_timestamp


def test_combine() -> None:
	exchanges = example_exchanges()
	groups    = group_by_timestamp(cast(list[Transaction], exchanges)).values()
	combined  = [combine(cast(list[Exchange], g)) for g in groups]

	assert len(combined) == 0


def example_exchanges() -> list[Exchange]:
	# @TODO: add examples here
	return []
