---
title: Documentation Development
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
sidebar_position: 10
sidebar_class_name: hidden
---

## Documentation Structure

We aim to follow the [Diátaxis Framework](https://diataxis.fr/) where possible.
This framework specifies four distinct categories: Tutorials, Explanation, How-to Guides, and Reference.
As you contribute to the documentation, use the framework as a guide to help you decide where to add content.
We recognize that not everything will fall into the four categories and welcome suggestions on how to improve the documentation to make it more useful for everyone.

## Checkout and Serve Docs Locally

Follow the steps below to work locally with this project.

1. Make sure you have a nodejs environment (>v16) set up locally.
1. Fork, clone or download this project.
1. Install node dependencies: `npm install`
1. Run `npm start` to run a local development server
1. View the docs at [http://localhost:3000](http://localhost:3000).
1. Make changes to the content of the site and preview them at the link above.

### <a name="add_a_new_page"></a>Add a New Page

You can add `.md` and `.mdx` files to this project to be rendered. Most pages are written in [Markdown](https://github.github.com/gfm/).

1. Go to the `docs/docs` folder and locate the section you'd like to update.
1. Create a new file called `my-page.md`. Use dashes as spaces in your file name.
1. Add [front matter](#front-matter) to your new file.
1. Add your [Markdown](https://github.github.com/gfm/) content.
1. If you've set up a dev environment, you can preview your new page on [http://localhost:3000](http://localhost:3000).

#### Front Matter

All pages require [front matter](https://docusaurus.io/docs/markdown-features#front-matter) to render properly. At a minimum you will need to specify:

- `title:` The title of the page.
- `description:` A brief description of the page content.
- `sidebar_position:` This controls how pages are displayed in menus and lists. The first file in each section should be named `index.md` and have a lower number. Use sequential numbers to control how pages get sorted in each section.
- **Optional** `slug:` This allows you to set this page's URL path. Ex. `/resources/plugins`
- **Optional** `sidebar_class_name:` CSS class name for styling the sidebar item. Use `hidden` to hide from sidebar.

**Example:**

```
---
title: My New Doc
description: A tutorial for getting started
sidebar_position: 2
---
```

### Add a New Section

1. Create a folder named `newsection` in the `docs/docs` directory.
1. [Create a new file](/contribute/docs#add_a_new_page) called `index.md`. Set the `sidebar_position:` of this page to `1` -- it'll be the home page for this section.
1. Add your [Markdown](https://github.github.com/gfm/) content. Since this is an index page it may be helpful to add some information about this new section. Create additional pages as needed and link to them from this page.
1. Docusaurus will automatically detect the new section and add it to the sidebar based on the folder structure and front matter configuration.

### Add Images

1. Create an `images` folder in your section.
1. Create an additional folder that matches the name of the document that contains images.
1. Add photos to this folder.
1. You can refer to them with `images/my-document/filename.jpg` in your pages.

### Add Table of Contents to a Page

Docusaurus automatically generates a table of contents from the headings in your document. You can read about its configuration [here](https://docusaurus.io/docs/markdown-features/toc).

The TOC is added to all pages by default. It can be customized by setting `toc_min_heading_level` and `toc_max_heading_level` in the front matter, or hidden completely by setting `hide_table_of_contents: true`.

## Check for Broken Links

You can check for broken links locally by building the documentation:

```
npm run build
```

Docusaurus will report any broken internal links during the build process. The build will fail if there are broken links, ensuring they are caught before deployment.

## Deploy

This project is deployed via Netlify using the steps defined in `netlify.toml` in the root of the Meltano project.

## Troubleshooting

### MDX Syntax Errors

If you encounter issues with special characters or JSX-like syntax in code blocks, you may need to use MDX-specific escaping. Docusaurus uses MDX, which allows you to use JSX in your Markdown files.

For code blocks with curly braces or other special characters, ensure they are properly fenced with triple backticks. If you need to use JSX components within your Markdown, save the file with a `.mdx` extension instead of `.md`.
