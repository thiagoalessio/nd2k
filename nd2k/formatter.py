from datetime import datetime
from .queries import is_a_purchase
from .types import Transaction, CSV, KoinlyTag
from .trade import Trade
from .swap import Swap
from .exchange import Exchange


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
			continue

		if isinstance(t, Exchange):
			rows.append(t.format())
			continue

		if isinstance(t, Swap):
			rows.append(t.format())
			continue

		rows.append(t.format())

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


def format_date(data: datetime) -> str:
	return data.strftime("%Y-%m-%d %H:%M:%S")
