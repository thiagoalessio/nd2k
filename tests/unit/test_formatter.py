from datetime import datetime
from nd2k import formatter


def test_format_date() -> None:
	date = datetime(1970, 3, 15, 23, 45, 56)
	assert formatter.format_date(date) == "1970-03-15 23:45:56"
