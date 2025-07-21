# Makefile for running tests in etl_pipeline project

.PHONY: unit integration end_to_end test clean

PYTHONPATH := $(shell pwd)/src
export PYTHONPATH

unit:
	@. .venv/bin/activate && PYTHONPATH=$(PYTHONPATH) python -m pytest -m "not integration and not end_to_end" -ra

integration:
	@. .venv/bin/activate && PYTHONPATH=$(PYTHONPATH) pytest -m "integration" -ra

end_to_end:
	@. .venv/bin/activate && PYTHONPATH=$(PYTHONPATH) pytest -m "end_to_end" -ra

test: unit integration end_to_end

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
