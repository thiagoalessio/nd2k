from .types import Transaction, CSV
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
			rows.append(t.format())
			continue

		if isinstance(t, Exchange):
			rows.append(t.format())
			continue

		if isinstance(t, Swap):
			rows.append(t.format())
			continue

		rows.append(t.format())

	return rows
