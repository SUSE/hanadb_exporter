default: deps test

deps:
	pip install tox

test:
	tox -e py

test-all:
	tox

coverage: tests/coverage.xml tests/htmlcov tests/.coverage
tests/coverage.xml tests/htmlcov tests/.coverage:
	tox -e coverage

clean:
	rm -rf .tox tests/{coverage.xml,.coverage,htmlcov}

.PHONY: clean coverage deps test test-all
