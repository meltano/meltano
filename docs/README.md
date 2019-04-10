# Meltano Documentation

The live site can be found at: [https://www.meltano.com](https://www.meltano.com).

## Requirements

- [NodeJS 8+](https://nodejs.org/)

## Instructions

1. Clone this repo `git@gitlab.com:meltano/meltano.git`
1. Navigate to root directory in terminal
1. Install all dependencies
```bash
npm install
```
4. Run a local instance of VuePress that dynamically uploads as you make changes to the files in the `/docs` directory
```bash
npm run dev:docs
```

5. To view changes, go to http://localhost:8080/ (Troubleshooting: if 8080 doesn't work, check the success message for the correct port)

## Build Artifacts

To build the artifacts for the docs site, run the following commands:

1. Install all dependencies
```bash
npm install
```
2. Run a local instance of VuePress that dynamically uploads as you make changes to the files in the `/docs` directory
```bash
npm run build:docs
```
