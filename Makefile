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
base_image_tag = ${DOCKER_REGISTRY}/meltano/base
app_image_tag = ${DOCKER_REGISTRY}/meltano/meltano
runner_image_tag = ${DOCKER_REGISTRY}/meltano/runner
else
base_image_tag = meltano/base
app_image_tag = meltano/meltano
runner_image_tag = meltano/runner
endif

DOCKER_RUN=docker run -it --rm -v $(shell pwd):/app -w /app
PYTHON_RUN=${DOCKER_RUN} --name python-$(shell uuidgen) python
DCR=docker-compose run --rm
DCRN=${DCR} --no-deps

.PHONY: build test init_db clean docker_images

build: ui api

test:
	${DCRN} api ./setup.py test

init_db:
	${DCR} api python -m meltano.api.init_db

# pip related
TO_CLEAN  = ./build ./dist ./*.pyc ./*.tgz ./*.egg-info
# node_modules
TO_CLEAN += ./src/meltano_api/node_modules
TO_CLEAN += ./src/meltano_ui/node_modules
TO_CLEAN += ./src/meltano_ui/dist

clean:
	# rm is run inside a container to support cross-platform volume mount permissions.
	# see: https://github.com/moby/moby/issues/2259
	${PYTHON_RUN} bash -c 'rm -rf ${TO_CLEAN}'
	docker rmi -f ${base_image_tag}
	docker rmi -f ${app_image_tag}
	docker rmi -f ${runner_image_tag}

docker_images: base_image prod_image runner_image

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
		.

runner_image:
	docker build \
		--file docker/runner/Dockerfile \
		-t $(runner_image_tag) \
	  .

# API Related
# ===========
#
# - `make api` assembles all the necessary dependencies to run the API

.PHONY: api

MELTANO_API = src/meltano/api

api: prod_image ${MELTANO_API}/node_modules

${MELTANO_API}/node_modules:
	${DCRN} -w /meltano/${MELTANO_API} api yarn

# Pip Related
# ===========
#
# - `make requirements.txt` pins dependency versions. We use requirements.txt
#   as a lockfile essentially.

requirements.txt: setup.py
	${PYTHON_RUN} bash -c 'pip install -e .[api] && pip freeze --exclude-editable > $@'

# UI Related Tasks
# =================
#
# - `make ui` assembles the necessary UI dependencies and builds the static UI
#   artifacts to ui/dist
# - `make ui_*` will run a task from the scripts section of ui/package.json.
#   For instance `make ui_lint` will run the the UI's `yarn run lint`

.PHONY: ui ui_%

MELTANO_UI = src/meltano_ui

ui: ${MELTANO_UI}/dist

ui_%:
	${DCRN} ui yarn run $(@:ui_%=%)

${MELTANO_UI}/node_modules: ${MELTANO_UI}/yarn.lock
	${DCRN} ui yarn

APP_DEPS = ${MELTANO_UI}/node_modules
APP_DEPS += ${MELTANO_UI}/build ${MELTANO_UI}/config ${MELTANO_UI}/.babelrc
APP_DEPS += $(wildcard ${MELTANO_UI}/*.js)
APP_DEPS += $(wildcard ${MELTANO_UI}/*.json)
APP_DEPS += $(wildcard ${MELTANO_UI}/*.html)

${MELTANO_UI}/dist: ${APP_DEPS}
	${MAKE} ui_build

# Docs Related Tasks
# ==================
#
# - `make explain_makefile` will bring up a web server with this makefile annotated.

.PHONY: makefile_docs

explain_makefile:
	docker stop explain_makefile || echo 'booting server'
	${DOCKER_RUN} --name explain_makefile -p 8081:8081 node ./Makefile_explain.sh
