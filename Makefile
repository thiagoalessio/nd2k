all: test coverage type-checker complexity-metrics security-scan

clean:
	rm -rf build dist nd2k.egg-info

deps:
	pip install -r requirements-dev.txt

build: clean
	python -m build

build-container:
	podman build -t nd2k .

publish-to-pypi:
	flit publish

install:
	flit install

test:
	pytest tests/

coverage:
	pytest --cov=nd2k --cov=tests --cov-branch --cov-report=xml tests/

coverage-html:
	pytest --cov=nd2k --cov=tests --cov-branch --cov-report=html tests/

type-checker:
	mypy nd2k tests --strict

complexity-metrics:
	radon cc nd2k tests --show-complexity --total-average
	radon mi nd2k tests --show

security-scan:
	bandit -c pyproject.toml -r .
