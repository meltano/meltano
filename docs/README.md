# Meltano Documentation

![Meltano Logo](static/img/meltano.svg)

## Contribute to the Docs

Follow the steps below to work locally with this project.

1. Fork, clone or download this project.
2. Install node dependencies: `npm install`
3. Run `npm start` to run a local development server
4. View the docs at [http://localhost:3000](http://localhost:3000).
5. Make changes to the content of the site and preview them at the link above.

### Website

This website is built using [Docusaurus 2](https://docusaurus.io/), a modern static website generator.

Add/edit category icon as a base64 svg in `_category_.json`
To highlight a line of code, add `==` before it, eg. `==mkdir meltano-projects`

Read the [Docusaurus guides](https://docusaurus.io/docs/category/guides) for any further information.

### Build

```sh
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Deployment

Using SSH:

```sh
USE_SSH=true npm deploy
```

Not using SSH:

```sh
GIT_USER=<Your GitHub username> npm deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
