---
title: Documentation Development
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

## Documentation

The Meltano Documentation is built with Jekyll. Please see the `README.md` 

Meltano uses [VuePress](https://vuepress.vuejs.org/) to manage its documentation site. Some of the benefits it provides us includes:

- Enhanced Markdown authoring experience
- Automatic check for broken relative links

### Text

Follow the [Merge Requests](#merge-requests) and [Changelog](#changelog) portions of this contribution section for text-based documentation contributions.

### Images

When adding supporting visuals to documentation, adhere to:

- Use Chrome in "incognito mode" (we do this to have the same browser bar for consistency across screenshots)
- Screenshot the image at 16:9 aspect ratio with minimum 1280x720px
- Place `.png` screenshot in `src/docs/.vuepress/public/screenshots/` with a descriptive name