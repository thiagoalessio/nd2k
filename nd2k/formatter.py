from .types import Transaction, CSV


def universal(transactions: list[Transaction]) -> CSV:
	rows = []
	rows.append([ # headers
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
	])
	for t in transactions:
		rows.append(t.format())
	return rows
