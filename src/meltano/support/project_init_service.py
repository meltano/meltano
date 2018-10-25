import os
import yaml
import click


class ProjectInitServiceError(Exception):
    pass


class ProjectInitService:
    def __init__(self, project_name):
        self.initialize_file = os.path.join(os.path.dirname(__file__), "initialize.yml")
        self.project = project_name.lower()

    def init(self):
        default_project_yaml = yaml.load(open(self.initialize_file))
        try:
            os.mkdir(self.project)
        except Exception as e:
            raise ProjectInitServiceError

        self.project_echo("", True)
        for name in default_project_yaml.keys():
            if name.startswith("/"):
                self.create_dir(name)
            else:
                self.create_file(name, default_project_yaml[name])

    def create_file(self, name, content):
        with open(self.join_with_project_base(name), "w") as f:
            f.write(content)
            self.project_echo(name, False, True)

    def create_dir(self, name):
        current_dir = name[1:]
        os.mkdir(os.path.join(".", self.project, current_dir))
        self.project_echo(current_dir, False, True)

    def project_echo(self, filename="", star=False, check=False):
        star = "⭐" if star else ""
        check = "✅" if check else ""
        click.secho(f"{star}{check}\tCreated", fg="blue", nl=False)
        click.echo(f" ./{self.project}/{filename}")

    def echo_instructions(self):
        click.secho(f"🚀\t{self.project}", fg="green", nl=False)
        click.echo(" has been created. Next steps:")
        click.echo(f"🚪\tcd ", nl=False)
        click.secho(self.project, fg="green")
        click.secho("🏃\tRun", nl=False)
        click.secho(" pip install", fg="green")
        click.echo("📖\tRead the Meltano README.", nl=False)
        click.secho(
            " https://gitlab.com/meltano/meltano/blob/master/README.md", fg="red"
        )
        click.echo("✏️\tEdit the meltano.yml file.")

    def join_with_project_base(self, filename):
        return os.path.join(".", self.project, filename)
