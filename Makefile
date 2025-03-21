all: test coverage lint complexity security

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

type-checker:
	mypy nd2k --strict

complexity-metrics:
	radon cc nd2k --show-complexity --total-average
	radon mi nd2k --show

security-scan:
	bandit -c pyproject.toml -r .

all-html: coverage-html lint-html security-html

coverage-html:
	mkdir -p reports
	pytest --cov=nd2k --cov=tests --cov-report=html:reports/pytest-cov tests/

lint-html:
	mkdir -p reports/mypy
	mypy nd2k --strict --html-report reports/mypy

security-html:
	mkdir -p reports
	bandit -c pyproject.toml -f html -r . > reports/bandit.html
