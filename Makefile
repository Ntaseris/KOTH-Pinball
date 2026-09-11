.PHONY: test test-verbose run

VENV = $(HOME)/mpfenv/bin/python

test:
	source $(HOME)/mpfenv/bin/activate && python -m unittest discover -s tests -v

test-verbose:
	source $(HOME)/mpfenv/bin/activate && python -m unittest discover -s tests -v 2>&1 | grep -E "^test_|FAIL|ERROR|OK$$|Ran "

run:
	source $(HOME)/mpfenv/bin/activate && mpf both -X
