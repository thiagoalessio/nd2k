all: test coverage-html lint type-checker complexity-metrics security-scan

clear-cache:
	find . -type d -name "__pycache__" -exec rm -r {} +

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
	pytest -vv -s --gherkin-terminal-reporter tests/

coverage:
	pytest -vv -s --gherkin-terminal-reporter \
		--cov=nd2k --cov=tests --cov-branch --cov-report=xml \
		tests/

coverage-html:
	pytest -vv -s --gherkin-terminal-reporter \
		--cov=nd2k --cov=tests --cov-branch --cov-report=html \
		tests/

lint:
	pyflakes nd2k tests

type-checker:
	mypy nd2k tests --strict

complexity-metrics:
	radon cc nd2k tests --show-complexity --total-average
	radon mi nd2k tests --show

security-scan:
	bandit -c pyproject.toml -r .
