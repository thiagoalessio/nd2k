import csv

from pathlib import Path
from typing import Any
from pytest_bdd import scenarios, given, when, then, parsers
from nd2k.main import entrypoint


DataTable = list[list[str]]


scenarios("./novadax_to_koinly.feature")


@given("a NovaDAX CSV file has the following operations:")
def create_input_file(tmp_path: Path, datatable: DataTable) -> None:
	file = tmp_path / "temp.csv"
	with file.open("w") as f:
		writer = csv.writer(f)
		writer.writerows(datatable)


@when("the file is processed")
def invoke_nd2k_tool(tmp_path: Path, monkeypatch: Any) -> None:
	file = tmp_path / "temp.csv"
	monkeypatch.setattr("sys.argv", ["nd2k", str(file)])
	entrypoint()


@then(parsers.parse('a Koinly {file_type} file should be created with the following transactions:'))
def compare_gerenared_file(tmp_path: Path, datatable: DataTable, file_type: str) -> None:
	file = tmp_path / f"temp_koinly_{file_type}.csv"
	with file.open("r") as f:
		result = list(csv.reader(f))
	assert datatable[1:] == result[1:] # ignoring headers
