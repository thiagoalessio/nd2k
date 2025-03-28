import pytest

from nd2k.utils import parse_trading_pair
from nd2k.types import TradingPair


def test_parse_trading_pair() -> None:
	data = "Compra(DOGE/BRL)"
	assert parse_trading_pair(data) == TradingPair(base="DOGE", quote="BRL")


def test_parse_trading_pair_invalid() -> None:
	data = "AnythingElse"
	with pytest.raises(ValueError) as e:
		parse_trading_pair(data)
	assert str(e.value) == f"No trading pair found in \"{data}\""
