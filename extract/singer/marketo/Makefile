.PHONY: test test-quick run build mypy

APP_NAME=tap-marketo

build:
	@echo "Building app..."
	@time docker build -t ${APP_NAME} .

test:
	@echo "Running full test suite..."
	@time docker run \
					-e MARKETO_ENDPOINT -e MARKETO_IDENTITY \
					-e MARKETO_CLIENT_SECRET -e MARKETO_CLIENT_ID \
					${APP_NAME}  pytest -vv -x

test-quick:
	@echo "Running tests that don't require a real API..."
	@time docker run ${APP_NAME} pytest -vv -k TestMarketoUtils

run:
	@echo "Running tap-marketo..."
	@time docker run \
					-e MARKETO_ENDPOINT -e MARKETO_IDENTITY \
					-e MARKETO_CLIENT_SECRET -e MARKETO_CLIENT_ID \
					${APP_NAME}  /bin/bash -c "tap-marketo create_keyfile --minute_offset 30; tap-marketo extract"

dry-run:
	@echo "Running tap-marketo..."
	@time docker run \
					-e MARKETO_ENDPOINT -e MARKETO_IDENTITY \
					-e MARKETO_CLIENT_SECRET -e MARKETO_CLIENT_ID \
					${APP_NAME}  /bin/bash -c "tap-marketo create_keyfile --minute_offset 30; tap-marketo extract --log_only True"

mypy:
	@echo "Running mypy for type-checking..."
	@time docker run ${APP_NAME} mypy tap_marketo --ignore-missing-imports

lint:
	@echo "Running linter..."
	@time black tap_marketo tests
