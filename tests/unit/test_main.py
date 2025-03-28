import pytest
import nd2k

from typing import Any


def test_no_input_file(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k"])
	with pytest.raises(SystemExit) as exc_info:
		nd2k.main.main()
	assert exc_info.value.code == 1
	assert "Usage: nd2k <novadax-csv>" in capsys.readouterr().out


def test_input_file_does_not_exist(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k", "invalid-file.csv"])
	with pytest.raises(SystemExit) as exc_info:
		nd2k.main.main()
	assert exc_info.value.code == 1
	assert "Error: No such file: invalid-file.csv" in capsys.readouterr().out


def test_version_short_form(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k", "-v"])
	with pytest.raises(SystemExit) as exc_info:
		nd2k.main.main()
	assert exc_info.value.code == 0
	assert nd2k.__version__ in capsys.readouterr().out


def test_version_long_form(capsys: Any, monkeypatch: Any) -> None:
	monkeypatch.setattr("sys.argv", ["nd2k", "--version"])
	with pytest.raises(SystemExit) as exc_info:
		nd2k.main.main()
	assert exc_info.value.code == 0
	assert nd2k.__version__ in capsys.readouterr().out
