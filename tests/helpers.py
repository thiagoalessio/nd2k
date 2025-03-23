from typing import Any
from datetime import datetime
from decimal import Decimal
from nd2k.types import (
	Operation,
	OperationType,
	Trade,
	TradeOperations,
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


def create_test_trade(**kwargs: Any) -> Trade:
	defaults = {
		"summary":      "Test",
		"operations":   TradeOperations(),
		"trading_pair": TradingPair(base="ABC", quote="XYZ"),
	}
	return Trade(**{**defaults, **kwargs})


# Normalize files before comparison:
# This ensures consistent line endings and encoding.
def normalize_file(file_path: str) -> None:
	with open(file_path, "r", encoding="utf-8") as f:
		content = f.read()

	with open(file_path, "w", encoding="utf-8", newline="\n") as f:
		f.write(content)
