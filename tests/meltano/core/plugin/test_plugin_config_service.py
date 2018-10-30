import json

from meltano.core.plugin.config_service import PluginConfigService


class TestPluginConfigService:
    subject_cls = PluginConfigService

    def test_envsubst(self, tmp_path):
        src = tmp_path.joinpath("src")
        dst = tmp_path.joinpath("dst")

        with src.open("w") as o:
            o.write(
                "{"
                '  "var": "$VAR",'
                '  "foo": "${FOO}",'
                '  "missing": "$MISSING",'
                '  "multiple": "$A ${B} $C"'
                "}"
            )

        env = {
            "VAR": "hello world!",
            "FOO": 42,
            "A": "rock",
            "B": "paper",
            "C": "scissors",
        }

        self.subject_cls.envsubst(src, dst, env=env)

        parsed_dst = json.load(dst.open())
        assert parsed_dst["var"] == env["VAR"]
        assert parsed_dst["foo"] == str(env["FOO"])
        assert parsed_dst["missing"] == ""
        assert parsed_dst["multiple"] == "rock paper scissors"
