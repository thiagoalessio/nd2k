import pytest

from nd2k import utils
from nd2k.types import TradingPair


def test_output_file() -> None:
	data     = "myfile.csv", "koinly_trades"
	actual   = utils.output_file(*data)
	expected = "myfile_koinly_trades.csv"
	assert actual == expected


def test_parse_trading_pair() -> None:
	data     = "Compra(PANDORA/BRL)"
	actual   = utils.parse_trading_pair(data)
	expected = TradingPair(base="PANDORA", quote="BRL")
	assert actual == expected


def test_parse_trading_pair_invalid() -> None:
	data = "AnythingElse"

	with pytest.raises(ValueError) as e:
		utils.parse_trading_pair(data)

	assert str(e.value) == f"No trading pair found in \"{data}\""
