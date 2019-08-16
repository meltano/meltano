# Meltano Documentation

Read more at [meltano.com](https://www.meltano.com).

## Prerequisites

Before you move on, make sure you have [Node 8.x]((https://nodejs.org/)) or newer installed.

## Instructions

1. Clone the project
```sh
git clone git@gitlab.com:meltano/meltano.git
```
2. Navigate to the `docs/` folder and install all dependencies 

```sh
cd meltano/docs/
npm install
```
3. Build and run
```bash
npm run dev:docs
```
4. View changes at http://localhost:8080/ 

## Build Artifacts

To generate static assets for the `docs/` directory, run:
```bash
npm run build:docs
```
This will add the generated files in the `docs/public` directory.

## FAQs

**1. How do I add screenshots?**

- Place the images in `/docs/.vuepress/public`.
- Use Markdown image syntax `![imageAltText](imageUrl)`
