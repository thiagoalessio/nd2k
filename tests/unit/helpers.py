from typing import Any
from datetime import datetime
from decimal import Decimal
from nd2k.types import (
	Operation,
	OperationType,
	PartialTrade,
	TradingPair,
)


def create_test_operation(**kwargs: Any) -> Operation:
	defaults = {
		"date":    datetime.now(),
		"type":    OperationType.BUY,
		"summary": "Test",
		"symbol":  "TST",
		"amount":  Decimal("1.234"),
		"status":  "Sucesso",
	}
	return Operation(**{**defaults, **kwargs})


def create_test_trade(**kwargs: Any) -> PartialTrade:
	defaults = {
		"summary":      "Test",
		"trading_pair": TradingPair(base="ABC", quote="XYZ"),
	}
	return PartialTrade(**{**defaults, **kwargs})
