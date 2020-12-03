import pytest
from unittest import mock

from meltano.core.plugin import PluginType, PluginDefinition, Variant, ProjectPlugin


class TestPluginDefinition:
    ATTRS = {
        "minimal": {"name": "tap-example", "namespace": "tap_example"},
        "basic": {
            "name": "tap-example",
            "namespace": "tap_example",
            "label": "Example",
            "variant": "meltano",
            "pip_url": "tap-example",
            "repo": "https://gitlab.com/meltano/tap-example",
            "foo": "bar",
            "baz": "qux",
        },
        "variants": {
            "name": "tap-example",
            "namespace": "tap_example",
            "foo": "bar",
            "variants": [
                {
                    "name": "meltano",
                    "pip_url": "meltano-tap-example",
                    "repo": "https://gitlab.com/meltano/tap-example",
                    "baz": "qux",
                },
                {
                    "name": "singer-io",
                    "original": True,
                    "deprecated": True,
                    "pip_url": "tap-example",
                    "repo": "https://github.com/singer-io/tap-example",
                },
            ],
        },
    }

    def test_init_minimal(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["minimal"])

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"
        assert plugin_def.hidden is None
        assert plugin_def.label is None
        assert plugin_def.logo_url is None
        assert plugin_def.description is None

        assert len(plugin_def.variants) == 1
        variant = plugin_def.current_variant
        assert variant == plugin_def.variants[0]

        assert plugin_def.current_variant_name == variant.name == None

    def test_init_basic(self):
        attrs = self.ATTRS["basic"]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"
        assert plugin_def.label == "Example"

        assert len(plugin_def.variants) == 1
        variant = plugin_def.current_variant
        assert variant == plugin_def.variants[0]

        assert plugin_def.current_variant_name == variant.name == "meltano"

        assert plugin_def.pip_url == variant.pip_url == attrs["pip_url"]
        assert plugin_def.repo == variant.repo == attrs["repo"]

        assert (
            plugin_def.all_extras == plugin_def.extras == {"foo": "bar", "baz": "qux"}
        )

    def test_init_variants(self):
        attrs = self.ATTRS["variants"]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"

        assert len(plugin_def.variants) == 2
        variant = plugin_def.current_variant
        assert variant == plugin_def.variants[0]

        assert plugin_def.current_variant_name == variant.name == "meltano"

        assert plugin_def.original == variant.original == None
        assert plugin_def.deprecated == variant.deprecated == None
        assert plugin_def.pip_url == variant.pip_url == attrs["variants"][0]["pip_url"]
        assert plugin_def.repo == variant.repo == attrs["variants"][0]["repo"]

        assert plugin_def.all_extras == {"foo": "bar", "baz": "qux"}
        assert plugin_def.extras == {"foo": "bar"}
        assert variant.extras == {"baz": "qux"}

        plugin_def.use_variant("singer-io")

        variant = plugin_def.current_variant
        assert variant == plugin_def.variants[1]

        assert plugin_def.current_variant_name == variant.name == "singer-io"

        assert plugin_def.original == variant.original == True
        assert plugin_def.deprecated == variant.deprecated == True
        assert plugin_def.pip_url == variant.pip_url == attrs["variants"][1]["pip_url"]
        assert plugin_def.repo == variant.repo == attrs["variants"][1]["repo"]

        assert plugin_def.all_extras == {"foo": "bar"}
        assert plugin_def.extras == {"foo": "bar"}
        assert variant.extras == {}

    @pytest.mark.parametrize("attrs_key", ATTRS.keys())
    def test_canonical(self, attrs_key):
        attrs = self.ATTRS[attrs_key]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)
        assert plugin_def.canonical() == attrs

    def test_use_variant(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["variants"])

        assert plugin_def.current_variant_name == "meltano"

        plugin_def.use_variant(Variant.ORIGINAL_NAME)
        assert plugin_def.current_variant_name == "singer-io"

        plugin_def.use_variant()
        assert plugin_def.current_variant_name == "meltano"

        plugin_def.use_variant(plugin_def.variants[1])
        assert plugin_def.current_variant_name == "singer-io"

    def list_variant_names(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["variants"])

        assert (
            plugin_def.list_variant_names()
            == "meltano (default), singer-io (deprecated)"
        )


class TestProjectPlugin:
    ATTRS = {
        "minimal": {"name": "tap-example"},
        "basic": {
            "name": "tap-example",
            "variant": "meltano",
            "pip_url": "tap-example",
            "config": {"foo": "bar"},
            "baz": "qux",
        },
        "custom": {
            "name": "tap-example",
            "namespace": "tap_example",
            "variant": "meltano",
            "pip_url": "tap-example",
            "repo": "https://gitlab.com/meltano/tap-example",
            "settings": [{"name": "foo"}],
            "config": {"foo": "bar"},
            "baz": "qux",
        },
    }

    def test_init_minimal(self):
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **self.ATTRS["minimal"])

        assert plugin.name == "tap-example"
        assert plugin.variant is None
        assert plugin.pip_url is None
        assert plugin.config == {}
        assert not plugin.is_custom()

    def test_init_basic(self):
        attrs = self.ATTRS["basic"]
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **attrs)

        assert plugin.name == "tap-example"
        assert plugin.variant == "meltano"
        assert plugin.pip_url == "tap-example"
        assert plugin.config == {"foo": "bar"}
        assert plugin.extras == {"baz": "qux"}
        assert not plugin.is_custom()

    def test_init_custom(self):
        attrs = self.ATTRS["custom"]
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **attrs)

        assert plugin.config == {"foo": "bar"}
        assert plugin.extras == {"baz": "qux"}

        assert plugin.is_custom()

        plugin_def = plugin.custom_definition
        variant = plugin_def.current_variant

        assert plugin_def.type == plugin.type
        assert plugin_def.name == plugin.name == attrs["name"]
        assert plugin_def.namespace == attrs["namespace"]
        assert plugin_def.settings[0].name == "foo"

        assert (
            plugin_def.current_variant_name
            == variant.name
            == plugin.variant
            == attrs["variant"]
        )

        assert (
            plugin_def.pip_url == variant.pip_url == plugin.pip_url == attrs["pip_url"]
        )
        assert plugin_def.repo == variant.repo == attrs["repo"]

        assert plugin_def.all_extras == plugin_def.extras == variant.extras == {}

    @pytest.mark.parametrize("attrs_key", ATTRS.keys())
    def test_canonical(self, attrs_key):
        attrs = self.ATTRS[attrs_key]
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **attrs)
        assert plugin.canonical() == attrs
