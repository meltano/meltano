---
title: Documentation Development
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

## Documentation Structure

We aim to follow the [Diátaxis Framework](https://diataxis.fr/) where possible.
This framework specifies four distinct categories: Tutorials, Explanation, How-to Guides, and Reference.
As you contribute to the documentation, use the framework as a guide to help you decide where to add content.
We recognize that not everything will fall into the four categories and welcome suggestions on how to improve the documentation to make it more useful for everyone.

## Checkout and Serve Docs Locally

Follow the steps below to work locally with this project.

1. Make sure you have a Ruby environment set up locally. You'll need the Ruby version specified in the `.gitlab-ci.yml` file.
1. Fork, clone or download this project.
1. Install ruby dependencies: `bundle install`
1. Install node dependencies: `npm install`
1. Build and preview: `bundle exec jekyll serve`
1. Preview the site at [http://127.0.0.1:4000](http://127.0.0.1:4000).
1. Make changes to the content of the site and preview them at the link above.

**Note:** Changes to `_config.yml` require you to stop the Jekyll server (`^C`) and restart it with `bundle exec jekyll serve`.

### Add a New Page

You can add `.md` and `.html` files to this project to be rendered. Most pages are written in [Markdown](https://github.github.com/gfm/).

1. Go to the `_src` folder and locate the section you'd like to update.
1. Create a new file called `my-page.md`. Use dashes as spaces in your file name.
1. Add [front matter](#front-matter) to your new file.
1. Add your [Markdown](https://github.github.com/gfm/) content.
1. If you've set up a dev environment, you can preview your new page on [http://127.0.0.1:4000](http://127.0.0.1:4000).

#### Front Matter

All pages require [front matter](https://jekyllrb.com/docs/front-matter/) to render properly. At a minimum you will need to specify:

- `layout:` The template file to use when rendering the content. For most pages use `doc`. Custom templates can be created and placed in `_layouts`.
- `title:` The title of the page.
- `weight:` This controls how pages are displayed in menus and lists. The first file in each section should be named `index.md` and have a weight of `1`. All other pages within a section should have a weight of `2`. You can use additional numbers to control how pages get sorted in each section.
- **Optional** `permalink:` This allows you to set this page's URL. You can use this to override Jekyll's automatically generated URLs. Ex. `/resources/plugins`

**Example:**

```
---
layout: doc
title: My New Doc
permalink: /tutorials/new-doc
weight: 2
---
```

### Add a New Section

1. Create a folder named `_newsection` in the `src` directory.
1. [Create a new file](#add-a-new-page) called `index.md`. Set the `weight:` of this page to `1` -- it'll be the home page for this section.
1. Add your [Markdown](https://github.github.com/gfm/) content. Since this is an index page it may be helpful to add some information about this new section. Create additional pages as needed and link to them from this page.
1. Update `collections:` in `_config.yml`. Ex:

```
  newsection:
    output: true
```

### Add Images

1. Create an `images` folder in your section.
1. Create an additional folder that matches the name of the document that contains images.
1. Add photos to this folder.
1. You can refer to them with `images/my-document/filename.jpg` in your pages.

### Add Table of Contents to a Page

The TOC is managed through the `jekyll-toc` gem. You can read about its configuration [here](https://github.com/toshimaru/jekyll-toc#customization).

This is added to all pages by default. It can be turned off by setting `toc: false` in the [fromt matter](https://jekyllrb.com/docs/front-matter/) of the document.

## Check for Broken Links

Builds will fail to deploy if links are broken. You can check for broken links locally with this command before pushing changes:

```
bundle exec jekyll build && bundle exec htmlproofer --log-level :debug ./_site/ --assume_extension --http_status_ignore 503 --url-ignore "/www.linkedin.com/,/localhost/"
```

If you'd like to skip external links, add `--disable-external`:

```
bundle exec jekyll build && bundle exec htmlproofer --log-level :debug ./_site/ --assume_extension --http_status_ignore 503 --url-ignore "/www.linkedin.com/,/localhost/" --disable-external
```

## Deploy

This project is deployed via Netlify using the steps defined in `netlify.toml` in the root of the Meltano project.

## Troubleshooting

### Liquid Syntax Error

You may receive an error on some pages when trying to use fenced code blocks:

```
Liquid Warning: Liquid syntax error (line 670): Expected end_of_string but found open_round in "{{ env_var('DBT_SOURCE_SCHEMA') }}" in $PATH/src/_reference/plugins.md
```

To fix this, wrap the code block in `{% raw %}` and `{% endraw %}` tags:

```
{% raw %}
meltano config <transform> set _vars <key> <value>

export <TRANSFORM>__VARS='{"<key>": "<value>"}'

# For example
meltano config --plugin-type=transform tap-gitlab set _vars schema "{{ env_var('DBT_SOURCE_SCHEMA') }}"

export TAP_GITLAB__VARS='{"schema": "{{ env_var(''DBT_SOURCE_SCHEMA'') }}"}'
{% endraw %}
```
