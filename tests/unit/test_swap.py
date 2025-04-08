from datetime import datetime
from decimal import Decimal
from typing import cast

from nd2k.swap import Swap, combine
from nd2k.transaction import Transaction, group_by_timestamp

from .helpers import fake_op


def test_combine() -> None:
	swaps    = example_swaps()
	groups   = group_by_timestamp(cast(list[Transaction], swaps)).values()
	combined = [combine(cast(list[Swap], g)) for g in groups]

	assert len(combined) == 3

	assert combined[0] == swaps[0] # s0

	# s1+s2
	assert combined[1].asset_a.amount == Decimal("266") # 127+139
	assert combined[1].asset_b.amount == Decimal("280") # 131+149

	assert combined[2] == swaps[3] # s3


def example_swaps() -> list[Swap]:
	now = datetime.now()

	s0 = Swap(
		asset_a=fake_op(summary="swap", symbol="AAA", amount=Decimal("109"), date=now),
		asset_b=fake_op(summary="swap", symbol="BBB", amount=Decimal("113"), date=now)
	)
	s1 = Swap(
		asset_a=fake_op(summary="swap", symbol="AAA", amount=Decimal("127"), date=now),
		asset_b=fake_op(summary="swap", symbol="CCC", amount=Decimal("131"), date=now)
	)
	s2 = Swap(
		asset_a=fake_op(summary="swap", symbol="AAA", amount=Decimal("139"), date=now),
		asset_b=fake_op(summary="swap", symbol="CCC", amount=Decimal("149"), date=now)
	)
	s3 = Swap(
		asset_a=fake_op(summary="swap", symbol="CCC", amount=Decimal("151"), date=now),
		asset_b=fake_op(summary="swap", symbol="DDD", amount=Decimal("157"), date=now)
	)
	return [s0, s1, s2, s3]
