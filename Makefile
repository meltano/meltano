# General
# =======
#
# - `make` or `make build` initializes the project
#   - Install node_modules needed by UI and API
#   - Build static UI artifacts
#   - Build all docker images needed for dev
# - `make test` runs pytest
# - `make init_db` initializes the db schema needed to run the API
# - `make clean` deletes all the build artifacts
# - `make docker_images` builds all the docker images including the production
#   image

ifdef DOCKER_REGISTRY
base_image_tag = ${DOCKER_REGISTRY}/meltano/meltano/base
app_image_tag = ${DOCKER_REGISTRY}/meltano/meltano
runner_image_tag = ${DOCKER_REGISTRY}/meltano/meltano/runner
cli_image_tag = ${DOCKER_REGISTRY}/meltano/meltano/runner
else
base_image_tag = meltano/meltano/base
app_image_tag = meltano/meltano
runner_image_tag = meltano/meltano/runner
cli_image_tag = meltano/meltano/cli
endif

DOCKER_RUN=docker run -it --rm -v $(shell pwd):/app -w /app
PYTHON_RUN=${DOCKER_RUN} --name python-$(shell uuidgen) python
DCR=docker-compose run --rm
DCRN=${DCR} --no-deps

MELTANO_WEBAPP = src/webapp
MELTANO_API = src/meltano/api
MELTANO_CORE_BUNDLE = src/meltano/core/bundle

.PHONY: build test init_db clean docker_images release

build: ui api

test:
	${DCRN} api ./setup.py test

init_db:
	${DCR} api python -m meltano.api.init_db

# pip related
TO_CLEAN  = ./build ./dist ./*.egg-info
# node_modules
TO_CLEAN += ./${MELTANO_API}/static/*
TO_CLEAN += ./${MELTANO_API}/templates/*
TO_CLEAN += ./${MELTANO_WEBAPP}/node_modules
TO_CLEAN += ./${MELTANO_WEBAPP}/dist

clean:
	rm -rf ${TO_CLEAN}

clean_bundle_models:
	rm -rf ${MELTANO_CORE_BUNDLE}/model/*

clean_all: clean
	docker rmi -f ${base_image_tag}
	docker rmi -f ${app_image_tag}
	docker rmi -f ${runner_image_tag}

docker_images: base_image prod_image cli_image runner_image

# Docker Image Related
# ====================
#
# - `make base_image` builds meltano/base
# - `make prod_image` builds meltano/meltano which is an all-in-one production
#   image that includes the static ui artifacts in the image.

.PHONY: base_image prod_image runner_image

base_image:
	docker build \
		--file docker/base/Dockerfile \
		-t $(base_image_tag) \
		.

prod_image: base_image ui
	docker build \
		--file docker/prod/Dockerfile \
		-t $(app_image_tag) \
		--build-arg BASE_IMAGE=$(base_image_tag) \
		.

cli_image:
	docker build \
		--file docker/cli/Dockerfile \
		-t $(cli_image_tag) \
		.

runner_image: cli_image
	docker build \
		--file docker/runner/Dockerfile \
		-t $(runner_image_tag) \
		--build-arg BASE_IMAGE=$(cli_image_tag) \
	  .

# API Related
# ===========
#
# - `make api` assembles all the necessary dependencies to run the API

.PHONY: api

api: prod_image ${MELTANO_API}/node_modules

${MELTANO_API}/node_modules:
	${DCRN} -w /meltano/${MELTANO_API} api yarn

# Packaging Related
# ===========
#
# - `make requirements.txt` pins dependency versions. We use requirements.txt
#   as a lockfile essentially.

requirements.txt: setup.py
	${PYTHON_RUN} bash -c 'pip install -e .[dev] && pip freeze --exclude-editable > $@'

MODELS := $(wildcard model/*.m5o)
MODELS := $(filter-out *.m5oc, $(MODELS)) # remove compiled files
MODELS_TARGETS := $(patsubst %, ${MELTANO_CORE_BUNDLE}/%, $(MODELS))

${MELTANO_CORE_BUNDLE}/model/%:
	mkdir -p $(@D)
	cp model/$* $@

bundle_ui: ui
	mkdir -p src/meltano/api/templates && \
	cp src/webapp/dist/index.html src/meltano/api/templates/webapp.html && \
	cp -r src/webapp/dist/. src/meltano/api/static && \
	rm src/meltano/api/index.html

freeze_db:
	scripts/alembic_freeze.py

.PHONY: bundle
bundle: bundle_ui

sdist: bundle freeze_db
	python setup.py sdist

docker_sdist: base_image
	docker run --rm -v `pwd`:/meltano ${base_image_tag} \
	bash -c "make sdist" && \
	bash -c "chmod 777 dist/*"

# UI Related Tasks
# =================
#
# - `make ui` assembles the necessary UI dependencies and builds the static UI
#   artifacts to ui/dist

.PHONY: ui

ui:
	cd src/webapp && yarn && yarn build

${MELTANO_WEBAPP}/node_modules: ${MELTANO_WEBAPP}/yarn.lock
	cd ${MELTANO_WEBAPP} && yarn install --frozen-lockfile


# Docs Related Tasks
# ==================
#

.PHONY: makefile_docs docs_image docs_shell

docs_image: base_image
	docker build \
		--file docker/docs/Dockerfile \
		-t meltano/docs_build \
		.

docs_shell: docs_image
	${DOCKER_RUN} -w /app/docs meltano/docs_build bash

docs/build: docs_image docs/source
	${DOCKER_RUN} -w /app/docs meltano/docs_build make html

docs/serve: docs/build
	${DOCKER_RUN} \
		-w /app/docs \
		-p 8080:8081 \
		meltano/docs_build sphinx-serve -b build

# Lint Related Tasks
# ==================
#

.PHONY: lint show_lint

BLACK_RUN = black src/meltano tests/ 
ESLINT_RUN = cd ${MELTANO_WEBAPP} && yarn run lint

lint_black:
	${BLACK_RUN}

lint_eslint: ${MELTANO_WEBAPP}/node_modules
	${ESLINT_RUN} --fix

show_lint_black:
	${BLACK_RUN} --check --diff

show_lint_eslint: ${MELTANO_WEBAPP}/node_modules
	${ESLINT_RUN}

lint: lint_black lint_eslint
show_lint: show_lint_black show_lint_eslint

# Makefile Related Tasks
# ======================
#
# - `make explain_makefile` will bring up a web server with this makefile annotated.
explain_makefile:
	docker stop explain_makefile || echo 'booting server'
	${DOCKER_RUN} --name explain_makefile -p 8081:8081 node ./Makefile_explain.sh

# Release
# =====================
ifdef type
  override type := --$(type)
endif

release:
	git diff --quiet || { echo "Working directory is dirty, please commit or stash your changes."; exit 1; } && \
	changelog release $(type) --yes && \
	git add CHANGELOG.md && \
	bumpversion --tag --allow-dirty --new-version `changelog current` minor
