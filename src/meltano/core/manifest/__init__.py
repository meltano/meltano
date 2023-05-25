"""Meltano manifest.

A Meltano manifest file is JSON file which representation of all information
required to describe a Meltano project. It conforms to the same schema used for
`meltano.yml`, and can be thought of as a pre-processed Meltano project file,
where most of the processing that would normally be done at run-time has
instead been done when the manifest file was compiled.

Manifest files always have a specific environment denoted in their name (i.e
`meltano-manifest.<Meltano environment name>.json`), or if the name is simply
`meltano-manifest.json` it represents running its Meltano project with no
active environment. As the environment selection is determined by which
manifest file is used, a manifest file will never have an `environments` field.

Like regular Meltano project files, manifest files should not contain secrets.
As such, they cannot be populated with values from environment variables, or
any other external source that may have sensitive data.

Unlike Meltano project files (which have `include_paths`), manifest files are
self-contained. Once a Meltano environment has been selected, there is no need
to reference any other file to fully describe the Meltano project.

Plugin lockfiles are merged into manifest files during compilation time.

Because the manifest file aims to be a single source of truth for project data,
and aims to enable significant simplication of `meltano.core`, few existing
`meltano.core` services are used for the compilation of the manifest file. In
the future, it should be the case that no `meltano.core` serivces are used for
the compilation of the manifest files.

Related: https://github.com/meltano/meltano/issues/7270

Unfortunately not all process can be done during the compilation process.
Things which still need to be processed when using a manifest file as a source
of information include:
- The merger and expansion of terminal env vars into a `.env` file, if one
  exists. Let the result of this merger be called env vars "A".
- The merger and expansion of env vars "A" into the job env, if a job is
  being run. Let the result of this merger be called env vars "B".
- The merger and expansion of env vars "B" into the schedule env, if a
  schedule is being run. Let the result of this merger be called env vars "C".
- The merger and expansion of env vars "C" into all other string fields of the
  manifest file (with exceptions) aside from the `plugins` field. This is the
  project-level env vars.
- The merger and expansion of the project-level env vars into a plugin env, if
  a plugin is being run. This is the plugin-level env vars.

Recognizing that this process is strictly hierarchical, the manifest module
provides a contexts submodule, which has context manager functions. These can
be used to establish an active manifest file, and then perform the necessary
processing for any call to get settings or env vars from the manifest within
the established context.

Under this paradigm, a function within `meltano.core` need not be provided the
job, schedule, plugin, etc. that it's working with. Instead the appropriate
contexts can be set by the caller, and the lower-level function can get values
of interest by requesting it from within the context. How exactly this will be
implemented is yet to be determined.

Related: https://github.com/meltano/meltano/issues/7271
"""

from __future__ import annotations

from meltano.core.manifest.manifest import Manifest
