# General
# =======
#
# - `make` or `make build` initializes the project
#   - Install node_modules needed by UI and API
#   - Build static UI artifacts
#   - Build all docker images needed for dev
# - `make test` runs pytest
# - `make clean` deletes all the build artifacts
# - `make docker_images` builds all the docker images including the production
#   image
#
# To build and publish:
#
# > make sdist-public
# > poetry publish --build

ifdef DOCKER_REGISTRY
base_image_tag = ${DOCKER_REGISTRY}/meltano/meltano/base
prod_image_tag = ${DOCKER_REGISTRY}/meltano/meltano
else
base_image_tag = meltano/meltano/base
prod_image_tag = meltano/meltano
endif

DOCKER_RUN=docker run -it --rm -v $(shell pwd):/app -w /app
PYTHON_RUN=${DOCKER_RUN} --name python-$(shell uuidgen) python
DCR=docker-compose run --rm
DCRN=${DCR} --no-deps

MELTANO_WEBAPP = src/webapp
MELTANO_API = src/meltano/api
MELTANO_RELEASE_MARKER_FILE = ./src/meltano/core/tracking/.release_marker

.PHONY: build test clean docker_images release help
.DEFAULT_GOAL := help

help: ## Display this help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

build: ui api ## Build the Meltano UI and API

test: ## Run the tests
	${DCRN} api poetry run pytest tests/

# pip related
TO_CLEAN  = ./build ./dist
# built UI
TO_CLEAN += ./${MELTANO_API}/static/js
TO_CLEAN += ./${MELTANO_API}/static/css
TO_CLEAN += ./${MELTANO_WEBAPP}/dist
# release marker
TO_CLEAN += ${MELTANO_RELEASE_MARKER_FILE}


clean: ## Delete build artifacts
	rm -rf ${TO_CLEAN}

docker_images: base_image prod_image ## Build the Meltano Docker images

docs: ## Serve docs
	cd docs &&\
	 bundle exec jekyll serve

# Docker Image Related
# ====================
#
# - `make base_image` builds meltano/base
# - `make prod_image` builds meltano/meltano which is an all-in-one production
#   image that includes the static ui artifacts in the image.

.PHONY: base_image prod_image docs

base_image: ## Build the Meltano base image
	docker build \
		--file docker/base/Dockerfile \
		-t $(base_image_tag) \
		.

prod_image: base_image ui ## Build the Meltano prod image
	docker build \
		--file docker/main/Dockerfile \
		-t $(prod_image_tag) \
		--build-arg BASE_IMAGE=$(base_image_tag) \
		.

# API Related
# ===========
#
# - `make api` assembles all the necessary dependencies to run the API

.PHONY: api

api: prod_image ${MELTANO_API}/node_modules ## Build the Meltano API

${MELTANO_API}/node_modules:
	${DCRN} -w /meltano/${MELTANO_API} api yarn

# Packaging Related
# ===========
#
# - `make lock` pins dependency versions. We use Poetry to generate
#   a lockfile.

lock: ## Update Poetry lock file
	poetry lock

bundle: clean ui ## Clean build artifacts, then build & bundle the UI
	mkdir -p src/meltano/api/templates && \
	cp src/webapp/dist/index.html src/meltano/api/templates/webapp.html && \
	cp src/webapp/dist/index-embed.html src/meltano/api/templates/embed.html && \
	cp -r src/webapp/dist/static/. src/meltano/api/static

freeze_db: ## Freeze the Meltano database to support DB migration during upgrades
	poetry run scripts/alembic_freeze.py

# sdist:
# Build the source distribution
# Note: plese use `sdist-public` for the actual release build
sdist: freeze_db bundle ## Build the Meltano sdist for development
	poetry build

# sdist_public:
# Same as sdist, except add release marker before poetry build
# The release marker differentiates installations 'in the wild' versus inernal dev builds and tests
sdist_public: freeze_db bundle ## Build the Meltano sdist for release
	touch src/meltano/core/tracking/.release_marker
	poetry build
	echo "Builds complete. You can now publish to PyPI using 'poetry publish'."

docker_sdist: base_image ## Build an image off of the base image that includes the Meltano sdist
	docker run --rm -v `pwd`:/meltano ${base_image_tag} \
	bash -c "make sdist" && \
	bash -c "chmod 777 dist/*"

# UI Related Tasks
# =================
#
# - `make ui` assembles the necessary UI dependencies and builds the static UI
#   artifacts to ui/dist

.PHONY: ui

ui: ## Build the Meltano UI
	cd src/webapp && yarn && yarn build

${MELTANO_WEBAPP}/node_modules: ${MELTANO_WEBAPP}/yarn.lock
	cd ${MELTANO_WEBAPP} && yarn install --frozen-lockfile


# Lint Related Tasks
# ==================
#

.PHONY: lint show_lint

TOX_RUN = poetry run tox -e
ESLINT_RUN = cd ${MELTANO_WEBAPP} && yarn run lint
JSON_YML_VALIDATE = poetry run python src/meltano/core/utils/validate_json_schema.py

args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

lint_python: ## Run Python linters & automatically apply fixes where possible
	${JSON_YML_VALIDATE}
	${TOX_RUN} fix -- $(call args)

lint_eslint: ${MELTANO_WEBAPP}/node_modules ## Run eslint & automatically apply fixes where possible
	${ESLINT_RUN} --fix

show_lint_python: ## Run Python linters & display output
	${TOX_RUN} lint -- $(call args)

show_lint_eslint: ${MELTANO_WEBAPP}/node_modules ## Run eslint & display output
	${ESLINT_RUN}

lint: lint_python lint_eslint ## Run linters & automatically apply fixes where possible
show_lint: show_lint_python show_lint_eslint ## Run linters & display output

# Release
# =====================
# Note:
# - this code is old and may be stale.
# - process currently runs in CI
release: ## Execute the automated steps of the deprecated release process
	git diff --quiet || { echo "Working directory is dirty, please commit or stash your changes."; exit 1; }
	yes | poetry run changelog release --$(type)
	git add CHANGELOG.md
	poetry run bumpversion --tag --allow-dirty --new-version `poetry run changelog current` $(type)
