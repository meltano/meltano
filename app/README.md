# melt

> meltano visualization with lookml files

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report

# run unit tests
npm run unit

# run e2e tests
npm run e2e

# run all tests
npm test
```

Or you can use yarn
``` bash
# install dependencies
yarn

# serve with hot reload at localhost:8080
yarn run dev

... etc ...
```

For a detailed explanation on how things work, check out the [guide](http://vuejs-templates.github.io/webpack/) and [docs for vue-loader](http://vuejs.github.io/vue-loader).

# Running the API

## First Time

Install dependencies
``` bash
# install dependencies
cd api
yarn
```

Open the python shell. `python`
```
cd api
python
```
From the shell:
```
from app import db
from models.settings import Settings

db.create_all()
settings = Settings()
db.session.add(settings)
db.session.commit()

exit()
```

From the project root:
```
pipenv install
```

## Run API For Real

```
pipenv shell
cd api
flask run
```