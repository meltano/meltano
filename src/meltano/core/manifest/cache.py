"""Store and retrieve Meltano manifests."""

# TODO: This module should handle reading/writing manifest files. Currently
# they're written by `meltano.cli.compile`, and not read by anything. Writing
# them is fairly simple, but reading is tricker because we need to decide
# whether we should read a manifest file from disk (if it exists), or generate
# a new one.
