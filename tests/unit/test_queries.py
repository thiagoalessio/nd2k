import pytest

from nd2k.operation import OperationType
from .helpers import fake_op, fake_partial_trade


def test_is_successful() -> None:
	assert fake_op(status="Sucesso").is_successful()
	assert not fake_op(status="Other").is_successful()


def test_is_a_non_trade() -> None:
	assert not fake_op(type=OperationType.BUY).is_a_non_trade()
	assert not fake_op(type=OperationType.SELL).is_a_non_trade()
	assert not fake_op(type=OperationType.TRADING_FEE).is_a_non_trade()
	assert not fake_op(type=OperationType.SWAP).is_a_non_trade()

	assert fake_op(type=OperationType.CRYPTO_DEPOSIT).is_a_non_trade()
	assert fake_op(type=OperationType.FIAT_DEPOSIT).is_a_non_trade()
	assert fake_op(type=OperationType.CRYPTO_WITHDRAW).is_a_non_trade()
	assert fake_op(type=OperationType.FIAT_WITHDRAW).is_a_non_trade()
	assert fake_op(type=OperationType.WITHDRAW_FEE).is_a_non_trade()
	assert fake_op(type=OperationType.REDEEMED_BONUS).is_a_non_trade()


def test_is_completed() -> None:
	assert fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = None,
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = fake_op(),
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = None,
		trading_fee = None,
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = fake_op(),
		trading_fee = None,
	).is_completed()
	assert not fake_partial_trade(
		base_asset  = None,
		quote_asset = None,
		trading_fee = fake_op(),
	).is_completed()


def test_fits_as_base_asset() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert tr.fits_as_base_asset(op)


def test_fits_as_base_asset_already_has_base() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_base_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_base_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_base_asset(op)


def test_fits_as_quote_asset() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_already_has_quote() -> None:
	tr = fake_partial_trade(
		quote_asset = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ"),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_wrong_summary() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="SELL(ABC/XYZ)", symbol="XYZ")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_quote_asset_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC"),
		trading_fee = fake_op(),
	)
	op = fake_op(summary="BUY(ABC/XYZ)", symbol="ABC")
	assert not tr.fits_as_quote_asset(op)


def test_fits_as_trading_fee_buy() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_already_has_fee() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(),
		quote_asset = fake_op(),
		trading_fee = fake_op(),
	)
	fee = fake_op(type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell_wrong_type() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.WITHDRAW_FEE)
	assert not tr.fits_as_trading_fee(op)


def test_fits_as_trading_fee_buy_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.BUY),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.BUY),
	)
	fee = fake_op(symbol="XYZ", type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_sell_wrong_symbol() -> None:
	tr = fake_partial_trade(
		base_asset  = fake_op(symbol="ABC", type=OperationType.SELL),
		quote_asset = fake_op(symbol="XYZ", type=OperationType.SELL),
	)
	fee = fake_op(symbol="ABC", type=OperationType.TRADING_FEE)
	assert not tr.fits_as_trading_fee(fee)


def test_fits_as_trading_fee_empty_trade() -> None:
	tr = fake_partial_trade()
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		tr.fits_as_trading_fee(op)
	assert str(e.value) == "Empty Trade"


def test_fits_as_trading_fee_malformed_trade() -> None:
	tr = fake_partial_trade(
		base_asset = fake_op(type=OperationType.CRYPTO_DEPOSIT),
	)
	op = fake_op(type=OperationType.TRADING_FEE)
	with pytest.raises(ValueError) as e:
		tr.fits_as_trading_fee(op)
	assert str(e.value) == "Malformed Trade"
