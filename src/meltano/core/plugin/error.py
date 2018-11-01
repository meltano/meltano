from meltano.core.error import PluginInstallWarning


class TapDiscoveryError(PluginInstallWarning):
    def __str__(self):
        return (
            "Running --discover on the tap failed, "
            "no catalog will be provided."
            "Some taps requires a valid catalog file "
            "with some selected streams."
        )
