import click
from . import cli
from .params import project

from meltano.core.compiler.project_compiler import ProjectCompiler


@cli.group(hidden=True, invoke_without_command=True)
@project
@click.pass_context
def model(ctx, project):
    compiler = ctx.obj["compiler"] = ProjectCompiler(project)
    compiler.parse()

    if ctx.invoked_subcommand is None:
        click.secho("Local", fg="green")
        for model in compiler.topics:
            click.echo(model["name"])

        print()

        click.secho("Packaged", fg="green")
        for model in compiler.package_topics:
            click.echo(model["name"])


@model.command()
@click.pass_context
def compile(ctx):
    compiler = ctx.obj["compiler"]

    compiler.compile()
    click.secho(f"Compiled {len(compiler.topics + compiler.package_topics)} model(s)")
