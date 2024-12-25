.PHONY: lint test run stop

lint:
	black .
	mypy .

test:
	PYTHONPATH=. pytest -v tests/

run:
	docker compose up --build

stop:
	docker compose down

