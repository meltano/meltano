---
title: Code Style Guide
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
hidden: true
---

## Code style

### Tools

Meltano uses the below tools to enforce consistent code style. Explore the [repo](https://github.com/meltano/meltano) to learn of the specific rules and settings of each.

Python:

- [isort](https://pycqa.github.io/isort/)
- [Black](https://github.com/ambv/black)
- [Flake8](https://flake8.pycqa.org/en/latest/)
- [wemake-python-styleguide](https://wemake-python-stylegui.de/en/latest/)
- [MyPy](https://mypy.readthedocs.io/en/stable/)

Flake8 is a python tool that glues together `pycodestyle`, `pyflakes`, `mccabe`, and third-party plugins to check the style and quality of python code,
and `wemake-python-styleguide` is a plugin for Flake8 that offers an extensive set of opinionated rules that encourage clean and correct code.

Javascript:

- [ESLint](https://eslint.org/docs/rules/)
- [ESLint Vue Plugin](https://github.com/vuejs/eslint-plugin-vue)
- [Prettier](https://prettier.io/)

You may use `make lint` to automatically lint all your code, or `make show_lint` if you only want to see what needs to change.

### Static typing

[MyPy is being adopted incrementally by this codebase](https://github.com/meltano/meltano/issues/6715). If you are adding new code, please use type hints.

If you are making changes to existing Python modules, you are encouraged to enable type checks. To do so,

- if you are fixing a single `.py` file inside a sub-package, e.g. `meltano.core.plugin.command`, _de-glob_ the sub-package in `pyproject.toml` and enumerate the files you are not touching. This will allow you to run `nox -rs mypy` and catch type errors only in the files you are touching.

  ```diff
    [[tool.mypy.overrides]]
    module = [
      ...
      "meltano.core.m5o.*",
  -   "meltano.core.plugin.*",
  +   "meltano.core.plugin.airflow",
  +   "meltano.core.plugin.base",
  +   # Note that meltano.core.plugin.command is not included here
  +   "meltano.core.plugin.config_service",
  +   "meltano.core.plugin.dbt.*",
  +   "meltano.core.plugin.error",
  +   "meltano.core.plugin.factory",
  +   "meltano.core.plugin.file",
  +   "meltano.core.plugin.meltano_file",
  +   "meltano.core.plugin.model.*",
  +   "meltano.core.plugin.project_plugin",
  +   "meltano.core.plugin.requirements",
  +   "meltano.core.plugin.settings_service",
  +   "meltano.core.plugin.singer.*",
  +   "meltano.core.plugin.superset",
  +   "meltano.core.plugin.utility",
      "meltano.core.runner.*",
      ...
    ]
  ```

- if you are fixing an entire sub-package, simply remove it from the ignore list.

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

<div class="notification is-danger">
  <p><strong>When testing your contributions you may need to ensure that your various `__pycache__` directories are removed. This helps ensure that you are running the code you expect to be running.</strong></p>
</div>

### Feature Flags

Sometimes it is useful to be able to make preview features available or allow deprecated features to be used for backwards compatibility.

To accomplish this, Meltano implements feature flags.

For new, deprecated, or experimental features, the relevant code path can be wrapped in a feature flag context. The process for adding new feature flags is as follows:

1. Determine a descriptive name for the feature flag and add it as a [`FeatureFlags` Enum value](https://github.com/meltano/meltano/blob/3237022624c9594852abe69acb4da3dbf1ce5c05/src/meltano/core/settings_service.py#L30)
1. Wrap your code blocks in a `ProjectSettingsService.feature_flag()` context as demonstrated below.
1. Add documentation about the new feature flag to the [Feature Flags section of the settings reference docs](/reference/settings#feature-flags)
1. In any documentation about the feature, note that the feature is experimental and link to the [Feature Flags section of the settings reference docs](/reference/settings#feature-flags). This note should be something similar to:
   > This feature is experimental and must be enabled using feature flags. See the docs here: ...
1. Add your feature flag metadata to [settings.yml](https://github.com/meltano/meltano/blob/3237022624c9594852abe69acb4da3dbf1ce5c05/src/meltano/core/bundle/settings.yml#L189) so that it is recognized as a project-wide configuration setting.

```python
# Example feature flag usage
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import FeatureFlags

class ExistingClass:

    def __init__(self):
        self.project = Project.find()
        self.settings_service = ProjectSettingsService(self.project)

    # If this method is called elsewhere in the code and the NEW_BEHAVIOR
    # feature flag is not set to 'true' it will throw an error:
    def experimental_method(self):
        with self.settings_service.feature_flag(FeatureFlags.NEW_BEHAVIOR):
            print("Doing new behavior...")

    # If this method is called elsewhere, its behavior will vary based on whether
    # the feature flag is set in the project
    # The same pattern can be used to deprecate existing behavior
    # Notice the "raise_error=False" in the feature_flag method call
    def existing_method_with_new_behavior(self):
        with self.settings_service.feature_flag(FeatureFlags.NEW_BEHAVIOR, raise_error=False) as new_behavior:
            if new_behavior:
                print("Doing the new behavior...")
            else:
                print("Doing the existing behavior...")
```
