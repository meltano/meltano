---
title: Code Style Guide
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

## Code style

### Tools

Meltano uses the below tools to enforce consistent code style. Explore the [repo](https://gitlab.com/meltano/meltano/tree/master) to learn of the specific rules and settings of each.

Python:
- [isort](https://pycqa.github.io/isort/)
- [Black](https://github.com/ambv/black)
- [Flake8](https://flake8.pycqa.org/en/latest/)
- [wemake-python-styleguide](https://wemake-python-stylegui.de/en/latest/)
- [MyPy](https://mypy.readthedocs.io/en/stable/)

Flake8 is a python tool that glues together `pycodestyle`, `pyflakes`, `mccabe`, and third-party plugins to check the style and quality of python code,
and `wemake-python-styleguide` is a plugin for Flake8 that offers an extensive set of opinionated rules that encourage clean and correct code.

MyPy is currently only executed as part of the build pipeline in order to avoid overwhelming developers with the complete list of violations. This allows for incremental and iterative improvement without requiring a concerted effort to fix all errors at once.

Javascript:
- [ESLint](https://eslint.org/docs/rules/)
- [ESLint Vue Plugin](https://github.com/vuejs/eslint-plugin-vue)
- [Prettier](https://prettier.io/)

You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

### Mantra

> A contributor should know the exact line-of-code to make a change based on convention

In the spirit of GitLab's "boring solutions" with the above tools and mantra, the codebase is additionally sorted as follows:

#### Imports

Javascript `import`s are sorted using the following pattern:

1. Code source location: third-party → local (separate each group with a single blank line)
1. Import scheme: Default imports → Partial imports
1. Name of the module, alphabetically: 'lodash' → 'vue'

<div class="notification is-warning">
  <p><strong>Tip: There should be only 2 blocks of imports with a single blank line between both blocks.
The first rule is used to separate both blocks.</strong></p>
</div>

```js
import lodash from 'lodash'                  // 1: third-party, 2: default, 3: [l]odash
import Vue from 'vue'                        // 1: third-party, 2: default, 3: [v]ue
import { bar, foo } from 'alib'              // 1: third-party, 2: partial, 3: [a]lib
import { mapAction, mapState } from 'vuex'   // 1: third-party, 2: partial, 3: [v]uex
¶  // 1 blank line to split import groups
import Widget from '@/component/Widget'      // 1: local, 2: default, 3: @/[c]omponent/Widget
import poller from '@/utils/poller'          // 1: local, 2: default, 3: @/[u]tils/poller
import { Medal } from '@/component/globals'  // 1: local, 2: partial, 3: @/[c]omponent/globals
import { bar, thing } from '@/utils/utils'   // 1: local, 2: partial, 3: @/[u]tils/utils
¶
¶  // 2 blank lines to split the imports from the code
```

Python imports are sorted automatically using [`isort`](https://pycqa.github.io/isort/). This is executed as part of the `make lint` command, as well as during execution of the pre-commit hook.

#### Definitions

Object properties and methods are alphabetical where `Vuex` stores are the exception (`defaultState` -> `getters` -> `actions` -> `mutations`)


<div class="notification is-warning">
  <p><strong>We are looking to automate these rules in https://gitlab.com/meltano/meltano/issues/1609.</strong></p>
</div>

<div class="notification is-danger">
  <p><strong>When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.</strong></p>
</div>

