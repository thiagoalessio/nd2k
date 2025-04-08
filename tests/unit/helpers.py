from typing import Any
from datetime import datetime
from decimal import Decimal
from nd2k.trade import PartialTrade, TradingPair
from nd2k.operation import OperationType, Operation


def fake_op(**kwargs: Any) -> Operation:
	defaults = {
		"date":    datetime.now(),
		"type":    OperationType.BUY,
		"summary": "Test",
		"symbol":  "TST",
		"amount":  Decimal("1.234"),
		"status":  "Sucesso",
	}
	return Operation(**{**defaults, **kwargs})


def fake_partial_trade(**kwargs: Any) -> PartialTrade:
	defaults = {
		"summary": "BUY(ABC/XYZ)",
		"trading_pair": TradingPair(base="ABC", quote="XYZ"),
	}
	return PartialTrade(**{**defaults, **kwargs})
