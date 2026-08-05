PYTHON ?= python3

.PHONY: check compile test

check: compile test

compile:
	PYTHONPATH=src $(PYTHON) -m compileall -q src tests

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
