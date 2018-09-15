## General
##########

BASE_PYTHON_DOCKERFILE_URL=https://raw.githubusercontent.com/docker-library/python/master/3.7/stretch/Dockerfile
BASE_NODE_DOCKERFILE_URL=https://raw.githubusercontent.com/nodejs/docker-node/master/10/stretch/Dockerfile

PYTHON_RUN=docker run -it --rm -v $(shell pwd):/app --name python-$(shell uuidgen) -w /app python
DCR=docker-compose run --rm
DCRN=${DCR} --no-deps

.PHONY: build

build: app api

images: app_image

## Python Related Tasks
####################

.PHONY: api init_db
.PHONY: base_image app_image

ifdef DOCKER_REGISTRY
base_image_tag = ${DOCKER_REGISTRY}/meltano/base
app_image_tag = ${DOCKER_REGSITRY}/meltano/meltano
else
base_image_tag = meltano/base
app_image_tag = meltano/meltano
endif

api: base_image
	docker-compose build api
	${MAKE} packages/api/node_modules

base_image: docker/base/Dockerfile
	docker build \
		--file docker/base/Dockerfile \
		-t $(base_image_tag) \
		.

app_image: base_image app
	${MAKE} packages/api/node_modules
	docker build \
		--file docker/app/Dockerfile \
		-t $(app_image_tag) \
		.

init_db:
	${DCR} api python -m api.init_db

packages/api/node_modules: packages/api/yarn.lock
	${DCRN} api bash -c 'cd api && yarn'

BASE_DF_DEPS = bin/build_dockerfile.py
BASE_DF_DEPS += docker/base/Dockerfile.template
BASE_DF_DEPS += docker/vendor/node/Dockerfile
BASE_DF_DEPS += docker/vendor/python/Dockerfile

docker/base/Dockerfile: ${BASE_DF_DEPS}
	${PYTHON_RUN} python -m bin.build_dockerfile docker/base/Dockerfile.template -o $@

docker/vendor/python/Dockerfile: docker/vendor/python/keyservers.patch
	echo '# DO NOT EDIT ME' > $@
	echo '# I am from ${BASE_PYTHON_DOCKERFILE_URL}' >> $@
	curl ${BASE_PYTHON_DOCKERFILE_URL} >> $@
	git apply docker/vendor/python/keyservers.patch

docker/vendor/node/Dockerfile:
	echo '# DO NOT EDIT ME' > $@
	echo '# I am from ${BASE_NODE_DOCKERFILE_URL}' >> $@
	curl ${BASE_NODE_DOCKERFILE_URL} >> $@

### Pip Related
###############

requirements.txt: setup.py
	${PYTHON_RUN} bash -c 'pip install pip-tools && pip-compile setup.py --output-file $@'

## App Related Tasks
####################

.PHONY: app app_%

app: app/dist

APP_DEPS = app/node_modules
APP_DEPS += app/build app/config app/.babelrc
APP_DEPS += $(wildcard app/*.js)
APP_DEPS += $(wildcard app/*.json)
APP_DEPS += $(wildcard app/*.html)

app/dist: ${APP_DEPS}
	${MAKE} app_build

app/node_modules: app/yarn.lock
	${DCRN} app yarn

# example: `make app_lint` will run `yarn run lint`
app_%:
	${DCRN} app yarn run $(@:app_%=%)
