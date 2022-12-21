from __future__ import annotations

import pytest

from meltano.core.plugin import BasePlugin, PluginDefinition, PluginType, Variant
from meltano.core.plugin.project_plugin import CyclicInheritanceError, ProjectPlugin
from meltano.core.plugin.requirements import PluginRequirement
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.utils import find_named


@pytest.mark.order(0)
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
            "description": "tap-example description",
            "logo_url": "path/to/tap_example_logo.jpg",
            "requires": {
                "files": [
                    {
                        "name": "files-example",
                        "variant": "meltano",
                    },
                ],
            },
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
                    "requires": {
                        "files": [
                            {
                                "name": "files-example",
                                "variant": "meltano",
                            },
                        ],
                    },
                },
                {
                    "name": "singer-io",
                    "original": True,
                    "deprecated": True,
                    "pip_url": "tap-example",
                    "repo": "https://github.com/singer-io/tap-example",
                    "requires": {
                        "files": [
                            {
                                "name": "files-example",
                                "variant": "singer-io",
                            },
                        ],
                    },
                },
            ],
        },
    }

    def test_init_minimal(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["minimal"])

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"
        assert plugin_def.hidden is None
        assert plugin_def.label == "tap-example"
        assert plugin_def.logo_url == "/static/logos/example-logo.png"
        assert plugin_def.description is None

        assert len(plugin_def.variants) == 1

        variant = plugin_def.variants[0]
        assert variant.name is None

    def test_init_basic(self):
        attrs = self.ATTRS["basic"]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"
        assert plugin_def.label == "Example"

        assert len(plugin_def.variants) == 1

        variant = plugin_def.variants[0]
        assert variant.name == "meltano"

        assert variant.pip_url == attrs["pip_url"]
        assert variant.repo == attrs["repo"]

        files_requirements = variant.requires[PluginType.FILES]
        assert isinstance(files_requirements[0], PluginRequirement)
        assert files_requirements[0].name == "files-example"
        assert files_requirements[0].variant == "meltano"

        assert plugin_def.extras == {"foo": "bar", "baz": "qux"}
        assert not variant.extras

    def test_init_variants(self):
        attrs = self.ATTRS["variants"]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)

        assert plugin_def.name == "tap-example"
        assert plugin_def.namespace == "tap_example"
        assert plugin_def.extras == {"foo": "bar"}

        assert len(plugin_def.variants) == 2

        variant = plugin_def.variants[0]
        assert variant.name == "meltano"

        assert variant.original is None
        assert variant.deprecated is None
        assert variant.pip_url == attrs["variants"][0]["pip_url"]
        assert variant.repo == attrs["variants"][0]["repo"]

        files_requirements = variant.requires[PluginType.FILES]
        assert isinstance(files_requirements[0], PluginRequirement)
        assert files_requirements[0].name == "files-example"
        assert files_requirements[0].variant == "meltano"

        assert variant.extras == {"baz": "qux"}

        variant = plugin_def.variants[1]
        assert variant.name == "singer-io"

        assert variant.original
        assert variant.deprecated
        assert variant.pip_url == attrs["variants"][1]["pip_url"]
        assert variant.repo == attrs["variants"][1]["repo"]

        files_requirements = variant.requires[PluginType.FILES]
        assert isinstance(files_requirements[0], PluginRequirement)
        assert files_requirements[0].name == "files-example"
        assert files_requirements[0].variant == "singer-io"

        assert not variant.extras

    @pytest.mark.parametrize("attrs_key", ATTRS.keys())
    def test_canonical(self, attrs_key):
        attrs = self.ATTRS[attrs_key]
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **attrs)
        assert plugin_def.canonical() == attrs

    def test_find_variant(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["variants"])

        assert plugin_def.find_variant().name == "meltano"

        assert plugin_def.find_variant(Variant.DEFAULT_NAME).name == "meltano"

        assert plugin_def.find_variant(Variant.ORIGINAL_NAME).name == "singer-io"

        assert plugin_def.find_variant(plugin_def.variants[1]).name == "singer-io"

    def test_variant_labels(self):
        plugin_def = PluginDefinition(PluginType.EXTRACTORS, **self.ATTRS["variants"])

        assert plugin_def.variant_labels == "meltano (default), singer-io (deprecated)"

    def test_label(self):
        plugin_def = PluginDefinition(
            PluginType.EXTRACTORS, name="tap-foo", namespace="tap_foo"
        )
        assert plugin_def.label == "tap-foo"

        plugin_def.label = "Foo"
        assert plugin_def.label == "Foo"

    def test_logo_url(self):
        plugin_def = PluginDefinition(
            PluginType.EXTRACTORS, name="tap-foo", namespace="tap_foo"
        )
        assert plugin_def.logo_url == "/static/logos/foo-logo.png"

        plugin_def.logo_url = "https://example.com/logo.svg"
        assert plugin_def.logo_url == "https://example.com/logo.svg"


class TestBasePlugin:
    @pytest.fixture
    def plugin_def(self):
        return PluginDefinition(
            PluginType.EXTRACTORS, **TestPluginDefinition.ATTRS["variants"]
        )

    @pytest.fixture
    def variant(self, plugin_def):
        return plugin_def.find_variant()

    @pytest.fixture
    def subject(self, plugin_def, variant):
        return BasePlugin(plugin_def, variant)

    def test_getattr(self, subject, plugin_def, variant):
        # Falls back to the plugin def
        assert subject.name == plugin_def.name

        # And the variant
        assert subject.pip_url == variant.pip_url

    def test_variant(self, subject, variant):
        assert subject.variant == variant.name

        variant.name = None
        assert subject.variant is None

    def test_extras(self, subject):
        assert subject.extras == {"foo": "bar", "baz": "qux"}

    def test_extra_settings(self, subject):
        subject.EXTRA_SETTINGS = [
            SettingDefinition(name="_foo", kind=SettingKind.PASSWORD, value="default"),
            SettingDefinition(name="_bar", kind=SettingKind.INTEGER, value=0),
        ]
        settings = subject.extra_settings

        # Known, overwritten in plugin/variant definition
        foo_setting = find_named(settings, "_foo")
        assert foo_setting
        assert foo_setting.kind == SettingKind.PASSWORD
        assert foo_setting.value == "bar"
        assert not foo_setting.is_custom

        # Known, not overwritten
        bar_setting = find_named(settings, "_bar")
        assert bar_setting
        assert bar_setting.kind == SettingKind.INTEGER
        assert bar_setting.value == 0
        assert not bar_setting.is_custom

        # Unknown, set in plugin/variant definition
        baz_setting = find_named(settings, "_baz")
        assert baz_setting
        assert baz_setting.kind is None
        assert baz_setting.value == "qux"
        assert not baz_setting.is_custom


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
            "executable": "example",
            "repo": "https://gitlab.com/meltano/tap-example",
            "settings": [{"name": "foo"}],
            "config": {"foo": "bar"},
            "baz": "qux",
        },
        "inherited": {
            "name": "tap-example-foo",
            "inherit_from": "tap-example",
            "variant": "meltano",
        },
        "complex_pip_url": {
            "name": "tap-example",
            "pip_url": (
                "--only-binary "
                "-i https://${PYPI_USER}:$PYPI_PASS@pypi.example.com/simple "
                "tap-example --pre"
            ),
        },
    }

    def test_init_minimal(self):
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **self.ATTRS["minimal"])

        assert plugin.name == "tap-example"
        assert plugin.variant is Variant.ORIGINAL_NAME
        assert plugin.pip_url is None
        assert not plugin.config
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
        variant = plugin.custom_definition.variants[0]

        assert plugin.parent._plugin_def is plugin_def
        assert plugin.parent._variant is variant

        assert plugin_def.type == plugin.type
        assert plugin_def.name == plugin.name == attrs["name"]
        assert plugin_def.namespace == attrs["namespace"]

        assert (
            plugin.settings[0].name
            == variant.settings[0].name
            == attrs["settings"][0]["name"]
        )

        assert plugin.variant == variant.name == attrs["variant"]

        assert plugin.pip_url == variant.pip_url == attrs["pip_url"]
        assert plugin.executable == variant.executable == attrs["executable"]
        assert plugin.repo == variant.repo == attrs["repo"]

        assert plugin_def.extras == variant.extras
        assert not plugin_def.extras

    def test_init_inherited(self):
        attrs = self.ATTRS["inherited"]
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **attrs)

        assert plugin.name == "tap-example-foo"
        assert plugin.inherit_from == "tap-example"
        assert plugin.variant == "meltano"

        # Defaults
        assert plugin.namespace == "tap_example_foo"
        assert plugin.label == plugin.name

    @pytest.mark.parametrize("attrs_key", ATTRS.keys())
    def test_canonical(self, attrs_key):
        attrs = self.ATTRS[attrs_key]
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **attrs)
        assert plugin.canonical() == attrs

    def test_parent(self, inherited_tap):
        tap = inherited_tap.parent
        assert isinstance(tap, ProjectPlugin)

        base_plugin = tap.parent
        assert isinstance(base_plugin, BasePlugin)

        # These attrs exist both on ProjectPlugin and PluginBase
        for attr in ("logo_url", "description", "variant", "pip_url", "executable"):
            # By default, they fall back on the parent
            assert (
                getattr(inherited_tap, attr)
                == getattr(tap, attr)
                == getattr(base_plugin, attr)
            )

            # Unless overwritten
            setattr(tap, attr, "tap_value")
            assert getattr(inherited_tap, attr) == getattr(tap, attr) == "tap_value"
            setattr(tap, attr, None)

            setattr(inherited_tap, attr, "inherited_tap_value")
            assert getattr(inherited_tap, attr) == "inherited_tap_value"
            setattr(inherited_tap, attr, None)

        # Plugins that explicitly inherit_from another plugin and
        # have their own unique name get their own namespace and label
        assert inherited_tap.namespace == "tap_mock_inherited"
        assert inherited_tap.label == "Mock: tap-mock-inherited"

        # Until overwritten
        inherited_tap.namespace = "inherited_tap_namespace"
        inherited_tap.label = "inherited_tap_label"
        assert inherited_tap.namespace == "inherited_tap_namespace"
        assert inherited_tap.label == "inherited_tap_label"
        inherited_tap.namespace = None
        inherited_tap.label = None

        # Shadowing plugins (with the same name as their parent) inherit namespace and label
        assert tap.namespace == base_plugin.namespace == "tap_mock"
        assert tap.label == base_plugin.label == "Mock"

        # Until overwritten
        tap.namespace = "tap_namespace"
        tap.label = "tap_label"
        assert tap.namespace == "tap_namespace"
        assert tap.label == "tap_label"
        tap.namespace = None
        tap.label = None

        # Attrs that only exist on PluginBase cannot be overwritten
        assert inherited_tap.repo == tap.repo == base_plugin.repo
        assert inherited_tap.docs == tap.docs == base_plugin.docs

    def test_set_parent(self):
        plugin_one = ProjectPlugin(
            PluginType.EXTRACTORS, name="tap-one", inherit_from="tap-two"
        )
        plugin_two = ProjectPlugin(
            PluginType.EXTRACTORS, name="tap-two", inherit_from="tap-three"
        )
        plugin_three = ProjectPlugin(
            PluginType.EXTRACTORS, name="tap-three", inherit_from="tap-one"
        )

        plugin_one.parent = plugin_two
        plugin_two.parent = plugin_three

        with pytest.raises(CyclicInheritanceError):
            plugin_three.parent = plugin_one

    def test_variant(self, plugin_discovery_service):
        # Without a variant set, the "original" name is used
        plugin = ProjectPlugin(PluginType.EXTRACTORS, name="tap-mock")
        assert plugin.variant == Variant.ORIGINAL_NAME

        # So that the original variant is found
        base_plugin = plugin_discovery_service.get_base_plugin(plugin)
        assert base_plugin._variant.original

        # Whose variant name is reflected once parent is set
        plugin.parent = base_plugin
        assert plugin.variant == base_plugin.variant == "singer-io"

        # With a variant set, that variant is used
        plugin = ProjectPlugin(
            PluginType.EXTRACTORS, name="tap-mock", variant="meltano"
        )
        assert plugin.variant == "meltano"

        base_plugin = plugin_discovery_service.get_base_plugin(plugin)
        plugin.parent = base_plugin

        assert plugin.variant == base_plugin.variant == "meltano"

    def test_command_inheritance(self, tap, inherited_tap, plugin_discovery_service):
        # variants
        assert tap.all_commands["cmd"].args == "cmd meltano"
        assert tap.all_commands["cmd"].description == "a description of cmd"

        assert tap.all_commands["cmd-variant"].args == "cmd-variant meltano"
        assert tap.all_commands["cmd-variant"].description is None

        assert tap.all_commands["test"].args == "--test"
        assert tap.all_commands["test"].description == "Run tests"
        assert tap.supported_commands == ["cmd", "cmd-variant", "test", "test_extra"]

        # inheritance
        assert inherited_tap.all_commands["cmd"].args == "cmd inherited"
        assert inherited_tap.all_commands["cmd-variant"].args == "cmd-variant meltano"
        assert inherited_tap.all_commands["cmd-inherited"].args == "cmd-inherited"
        assert inherited_tap.all_commands["test"].args == "--test"
        assert inherited_tap.supported_commands == [
            "cmd",
            "cmd-variant",
            "test",
            "test_extra",
            "cmd-inherited",
        ]

    def test_command_test(self, tap: BasePlugin):
        """Validate the plugin 'test' command."""
        assert "test" in tap.test_commands
        assert tap.test_commands["test"].args == "--test"
        assert tap.test_commands["test"].description == "Run tests"

        assert "test_extra" in tap.test_commands
        assert tap.test_commands["test_extra"].args == "test_extra"
        assert tap.test_commands["test_extra"].description == "Run extra tests"
        assert tap.test_commands["test_extra"].executable == "test-extra"

    def testenv_prefixes(self, inherited_tap, tap):
        assert tap.env_prefixes() == ["tap-mock", "tap_mock"]
        assert tap.env_prefixes(for_writing=True) == [
            "tap-mock",
            "tap_mock",
            "meltano_extract",
        ]

        assert inherited_tap.env_prefixes() == [
            "tap-mock-inherited",
            "tap_mock_inherited",
        ]
        assert inherited_tap.env_prefixes(for_writing=True) == [
            "tap-mock-inherited",
            "tap_mock_inherited",
            "tap-mock",
            "tap_mock",
            "meltano_extract",
        ]

    def test_config_with_extras(self):
        plugin = ProjectPlugin(PluginType.EXTRACTORS, **self.ATTRS["basic"])

        # It reads by combining config with extras (prefixed with _)
        config_with_extras = plugin.config_with_extras
        assert config_with_extras == {"foo": "bar", "_baz": "qux"}

        config_with_extras["foo"] = "BAR"
        config_with_extras["_baz"] = "QUX"

        config_with_extras["bar"] = "FOO"
        config_with_extras["_qux"] = "BAZ"

        # It writes by splitting based on the _ prefix and writing config and extras
        plugin.config_with_extras = config_with_extras

        assert plugin.config == {"foo": "BAR", "bar": "FOO"}
        assert plugin.extras == {"baz": "QUX", "qux": "BAZ"}

    def test_settings(self, tap):
        tap.config["custom"] = "from_meltano_yml"
        tap.config["nested"] = {"custom": True}

        settings_by_name = {setting.name: setting for setting in tap.all_settings}

        # Regular settings
        assert "test" in settings_by_name
        assert "start_date" in settings_by_name

        # Custom settings
        assert "custom" in settings_by_name
        assert "nested.custom" in settings_by_name
        assert settings_by_name["nested.custom"].kind == SettingKind.BOOLEAN

    def test_extra_settings(self, tap):
        tap.extras["custom"] = "from_meltano_yml"
        tap.extras["nested"] = {"custom": True}

        settings_by_name = {setting.name: setting for setting in tap.extra_settings}

        # Regular extras
        assert "_select" in settings_by_name
        assert "_catalog" in settings_by_name

        # Custom extras
        assert "_custom" in settings_by_name
        assert "_nested.custom" in settings_by_name
        assert settings_by_name["_nested.custom"].kind == SettingKind.BOOLEAN

    def test_requirements(self, transformer: ProjectPlugin):
        """Validate the plugin requirements."""
        assert transformer.all_requires
        requirement = transformer.all_requires[PluginType.FILES][0]
        assert requirement.name == "files-transformer-mock"
        assert requirement.variant == "meltano"

        # Plugin doesn't have any utility requirements
        assert not transformer.all_requires[PluginType.UTILITIES]


class TestPluginType:
    def test_properties(self):
        for plugin_type in PluginType:
            # assert no exceptions raised:
            assert plugin_type.descriptor is not None
            assert plugin_type.singular is not None
            assert plugin_type.verb is not None

    def test_specfic_properties(self):
        assert PluginType.FILES.descriptor == "file bundle"
        assert PluginType.TRANSFORMS.verb == "transform"
        assert PluginType.UTILITIES.verb == "utilize"
        assert PluginType.UTILITIES.singular == "utility"
        assert PluginType.UTILITIES.verb == "utilize"
        assert PluginType.MAPPERS.singular == "mapper"
        assert PluginType.MAPPERS.verb == "map"

    def test_from_cli_argument(self):
        for plugin_type in PluginType:
            assert PluginType.from_cli_argument(plugin_type.value) == plugin_type
            assert PluginType.from_cli_argument(plugin_type.singular) == plugin_type

        with pytest.raises(ValueError):
            PluginType.from_cli_argument("unknown type")
