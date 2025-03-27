from pathlib import Path
from nd2k.main import read

# https://github.com/thiagoalessio/nd2k/issues/8
def test_handle_input_with_any_encoding(tmp_path: Path) -> None:
	file = tmp_path / "temp.csv"

	contents = (
		bytes("hea,ders,x\r", "ascii")
		+ "foo,".encode("latin-1")
		+ b"\x81\xff\xfe"
		+ "bar,".encode("cp1252")
		+ b"\x80"
		+ "test".encode("utf-8"))

	with file.open("wb") as f:
		f.write(contents)

	assert read(str(file)) == [["foo", "bar", "test"]]
