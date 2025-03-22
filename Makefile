all: test coverage type-checker complexity-metrics security-scan

clean:
	rm -rf build dist nd2k.egg-info

deps:
	pip install -r requirements-dev.txt

build: clean
	python -m build

install:
	flit install

test:
	pytest tests/

coverage:
	pytest --cov=nd2k --cov=tests --cov-branch --cov-report=xml tests/

coverage-html:
	pytest --cov=nd2k --cov=tests --cov-report=html tests/

type-checker:
	mypy nd2k --strict

complexity-metrics:
	radon cc nd2k --show-complexity --total-average
	radon mi nd2k --show

security-scan:
	bandit -c pyproject.toml -r .
