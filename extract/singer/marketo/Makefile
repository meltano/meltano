.PHONY: test test-quick run build

APP_NAME=tap-marketo

test:
	@echo "Not implemented yet..."

test-quick:
	@echo "Not implemented yet..."

run:
	@echo "Running Marketo Extractor..."
	@time docker run \
					-e MARKETO_ENDPOINT -e MARKETO_IDENTITY \
					-e MARKETO_CLIENT_SECRET -e MARKETO_CLIENT_ID \
					${APP_NAME} tap-marketo

build:
	@echo "Building app..."
	@time docker build -t ${APP_NAME} .
