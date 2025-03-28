from datetime import datetime
from .queries import is_a_purchase, is_sending_funds
from .types import Transaction, CSV, Trade, NonTrade, KoinlyTag


universal_csv_headers = [
	"Date",
	"Sent Amount",
	"Sent Currency",
	"Received Amount",
	"Received Currency",
	"Fee Amount",
	"Fee Currency",
	"Net Worth Amount",
	"Net Worth Currency",
	"Label",
	"Description",
]


def universal(transactions: list[Transaction]) -> CSV:
	rows = []
	rows.append(universal_csv_headers)

	for t in transactions:
		if isinstance(t, Trade):
			rows.append(format_trade(t))
		else:
			rows.append(format_non_trade(t))

	return rows


def format_trade(t: Trade) -> list[str]:
	if is_a_purchase(t):
		sent_amount = t.quote_asset.amount
		sent_symbol = t.quote_asset.symbol
		recv_amount = t.base_asset.amount
		recv_symbol = t.base_asset.symbol
	else:
		sent_amount = t.base_asset.amount
		sent_symbol = t.base_asset.symbol
		recv_amount = t.quote_asset.amount
		recv_symbol = t.quote_asset.symbol

	return [
		format_date(t.base_asset.date), # Date
		f"{sent_amount}",               # Sent Amount
		f"{sent_symbol}",               # Sent Currency
		f"{recv_amount}",               # Received Amount
		f"{recv_symbol}",               # Received Currency
		f"{t.trading_fee.amount}",      # Fee Amount
		f"{t.trading_fee.symbol}",      # Fee Currency
		"",                             # Net Worth Amount
		"",                             # Net Worth Currency
		KoinlyTag[t.type.name].value,   # Label
		t.base_asset.summary,           # Description
		"",                             # TxHash
	]


def format_non_trade(t: NonTrade) -> list[str]:
	op = t.operation

	if is_sending_funds(op):
		sent_amount = str(op.amount)
		sent_symbol = op.symbol
		recv_amount = ""
		recv_symbol = ""
	else:
		sent_amount = ""
		sent_symbol = ""
		recv_amount = str(op.amount)
		recv_symbol = op.symbol

	return [
		format_date(op.date),          # Date
		sent_amount,                   # Sent Amount
		sent_symbol,                   # Sent Currency
		recv_amount,                   # Received Amount
		recv_symbol,                   # Received Currency
		"",                            # Fee Amount
		"",                            # Fee Currency
		"",                            # Net Worth Amount
		"",                            # Net Worth Currency
		KoinlyTag[op.type.name].value, # Label
		op.summary,                    # Description
		"",                            # TxHash
	]


def format_date(data: datetime) -> str:
	return data.strftime("%Y-%m-%d %H:%M:%S")
