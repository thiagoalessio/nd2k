from collections import defaultdict
from .transaction import Transaction


CSV = list[list[str]]
TransactionGroups = defaultdict[str, list[Transaction]]
