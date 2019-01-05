def test_init(project):
    files = (
        project.root.joinpath(file).resolve()
        for file in (
            "meltano.yml",
            "README.md",
            ".gitignore",
            "transform/dbt_project.yml",
            "transform/profile/profiles.yml",
        )
    )

    dirs = (
        project.root.joinpath(dir)
        for dir in (
            ".meltano",
            "model",
            "extract",
            "load",
            "transform",
            "transform/profile",
            "analyze",
            "notebook",
            "orchestrate",
        )
    )

    for file in files:
        assert file.is_file()

    for dir in dirs:
        assert dir.is_dir()
