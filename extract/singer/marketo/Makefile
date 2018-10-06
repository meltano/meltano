.PHONY: test test-quick run build mypy

APP_NAME=tap-marketo

test:
	@echo "Not implemented yet..."

test-quick:
	@echo "Not implemented yet..."

run:
	@echo "Running tap-marketo..."
	@time docker run \
					-e MARKETO_ENDPOINT -e MARKETO_IDENTITY \
					-e MARKETO_CLIENT_SECRET -e MARKETO_CLIENT_ID \
					${APP_NAME}  /bin/bash -c "tap-marketo create_keyfile; tap-marketo extract"

build:
	@echo "Building app..."
	@time docker build -t ${APP_NAME} .

mypy:
	@echo "Running mypy for type-checking..."
	@time docker run ${APP_NAME} mypy tap_marketo --ignore-missing-imports
