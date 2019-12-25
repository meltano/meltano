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

.PHONY: build test clean docker_images release

build: ui api

test:
	${DCRN} api ./setup.py test

# pip related
TO_CLEAN  = ./build ./dist
# built UI
TO_CLEAN += ./${MELTANO_API}/static/js
TO_CLEAN += ./${MELTANO_API}/static/css
TO_CLEAN += ./${MELTANO_WEBAPP}/dist

clean:
	rm -rf ${TO_CLEAN}

docker_images: base_image prod_image

# Docker Image Related
# ====================
#
# - `make base_image` builds meltano/base
# - `make prod_image` builds meltano/meltano which is an all-in-one production
#   image that includes the static ui artifacts in the image.

.PHONY: base_image prod_image

base_image:
	docker build \
		--file docker/base/Dockerfile \
		-t $(base_image_tag) \
		.

prod_image: base_image ui
	docker build \
		--file docker/prod/Dockerfile \
		-t $(prod_image_tag) \
		--build-arg BASE_IMAGE=$(base_image_tag) \
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
	pip freeze --exclude-editable > $@

bundle: clean ui
	mkdir -p src/meltano/api/templates && \
	cp src/webapp/dist/index.html src/meltano/api/templates/webapp.html && \
	cp -r src/webapp/dist/static/. src/meltano/api/static

freeze_db:
	scripts/alembic_freeze.py

sdist: freeze_db bundle
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
	git diff --quiet || { echo "Working directory is dirty, please commit or stash your changes."; exit 1; }
	yes | changelog release $(type)
	git add CHANGELOG.md
	bumpversion --tag --allow-dirty --new-version `changelog current` minor
