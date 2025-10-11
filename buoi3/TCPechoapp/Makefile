PYTHON ?= python3
PORT ?= 8080
MODE ?= line

.PHONY: run-server run-client test bench lint

run-server:
	$(PYTHON) server.py --host 0.0.0.0 --port $(PORT) --mode $(MODE)

run-client:
	$(PYTHON) client.py --host 127.0.0.1 --port $(PORT) --mode $(MODE) --input inline --text "Hello"

test:
	$(PYTHON) tests/e2e_echo_runner.py

bench:
	$(PYTHON) scripts/bench.py --host 127.0.0.1 --port $(PORT) --mode $(MODE)

lint:
	$(PYTHON) -m py_compile server.py client.py tests/e2e_echo_runner.py scripts/bench.py
