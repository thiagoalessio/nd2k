from datetime import datetime, timedelta
from decimal import Decimal
from typing import cast

from nd2k.nontrade import NonTrade, combine
from nd2k.transaction import Transaction, group_by_timestamp

from .helpers import fake_op


def test_combine() -> None:
	nontrades = example_non_trades()
	groups    = group_by_timestamp(cast(list[Transaction], nontrades)).values()
	combined  = [combine(cast(list[NonTrade], g)) for g in groups]

	assert len(combined) == 6

	# nt0+nt1
	assert combined[0].operation.amount == Decimal("5") # 2+3

	assert combined[1] == nontrades[2] # nt2
	assert combined[2] == nontrades[3] # nt3
	assert combined[3] == nontrades[4] # nt4

	# nt5+nt7
	assert combined[4].operation.amount == Decimal("32") # 13+19

	assert combined[5] == nontrades[6] #nt6


def example_non_trades() -> list[NonTrade]:
	now = datetime.now()
	a_minute_ago = now - timedelta(minutes=1)

	nt0 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("2"),  date=now)
	nt1 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("3"),  date=now)
	nt2 = fake_op(summary="withdraw", symbol="BBB", amount=Decimal("5"),  date=now)
	nt3 = fake_op(summary="withdraw", symbol="AAA", amount=Decimal("7"),  date=a_minute_ago)
	nt4 = fake_op(summary="deposit",  symbol="AAA", amount=Decimal("11"), date=now)
	nt5 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("13"), date=now)
	nt6 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("17"), date=a_minute_ago)
	nt7 = fake_op(summary="deposit",  symbol="BBB", amount=Decimal("19"), date=now)

	return [NonTrade(operation=nt) for nt in [nt0, nt1, nt2, nt3, nt4, nt5, nt6, nt7]]
