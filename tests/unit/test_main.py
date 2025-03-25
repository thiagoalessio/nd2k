import pytest

from typing import Any
from nd2k import main


def test_entrypoint_no_input_file(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k"])

	with pytest.raises(SystemExit) as exc_info:
		main.entrypoint()

	assert exc_info.value.code == 1
	assert "Usage: nd2k <novadax-csv>" in capsys.readouterr().out


def test_entrypoint_input_file_does_not_exist(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k", "invalid-file.csv"])

	with pytest.raises(SystemExit) as exc_info:
		main.entrypoint()

	assert exc_info.value.code == 1
	assert "Error: No such file: invalid-file.csv" in capsys.readouterr().out
