import pytest

from nd2k import queries as q
from nd2k.types import OperationType
from .helpers import fake_op, fake_partial_trade


def test_is_successful() -> None:
	assert q.is_successful(fake_op(status="Sucesso"))
	assert not q.is_successful(fake_op(status="Other"))


def test_is_part_of_a_trade() -> None:
	assert q.is_part_of_a_trade(fake_op(type=OperationType.BUY))
	assert q.is_part_of_a_trade(fake_op(type=OperationType.SELL))
	assert q.is_part_of_a_trade(fake_op(type=OperationType.TRADING_FEE))

	assert not q.is_part_of_a_trade(fake_op(type=OperationType.CRYPTO_DEPOSIT))
	assert not q.is_part_of_a_trade(fake_op(type=OperationType.FIAT_DEPOSIT))
	assert not q.is_part_of_a_trade(fake_op(type=OperationType.CRYPTO_WITHDRAW))
	assert not q.is_part_of_a_trade(fake_op(type=OperationType.FIAT_WITHDRAW))
	assert not q.is_part_of_a_trade(fake_op(type=OperationType.WITHDRAW_FEE))
	assert not q.is_part_of_a_trade(fake_op(type=OperationType.REDEEMED_BONUS))


def test_is_completed() -> None:
	assert q.is_completed(fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = None,
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = fake_op(),
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = None,
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = None,
	))
	assert not q.is_completed(fake_partial_trade(
		base_asset  = None,
		quote_asset = None,
		trading_fee = fake_op(),
	))


def test_fits_as_base_asset() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert q.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_already_has_base() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not q.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="ABC")
	assert not q.fits_as_base_asset(op, tr)


def test_fits_as_base_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not q.fits_as_base_asset(op, tr)


def test_fits_as_quote_asset() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert q.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_already_has_quote() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not q.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="XYZ")
	assert not q.fits_as_quote_asset(op, tr)


def test_fits_as_quote_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not q.fits_as_quote_asset(op, tr)


def test_fits_as_trading_fee_buy() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert q.fits_as_trading_fee(fee, tr)


def test_fits_as_trading_fee_sell() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert q.fits_as_trading_fee(fee, tr)


def test_fits_as_trading_fee_already_has_fee() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	)
	fee = fake_op(type=OperationType.TRADING_FEE)
	assert not q.fits_as_trading_fee(fee, tr)


def test_fits_as_trading_fee_sell_wrong_type() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.WITHDRAW_FEE)
	assert not q.fits_as_trading_fee(op, tr)


def test_fits_as_trading_fee_buy_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert not q.fits_as_trading_fee(fee, tr)


def test_fits_as_trading_fee_sell_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert not q.fits_as_trading_fee(fee, tr)


def test_fits_as_trading_fee_empty_trade() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		q.fits_as_trading_fee(op, tr)
	assert str(e.value) == "Empty Trade"


def test_fits_as_trading_fee_malformed_trade() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(type=OperationType.CRYPTO_DEPOSIT),
	)
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		q.fits_as_trading_fee(op, tr)
	assert str(e.value) == "Malformed Trade"
