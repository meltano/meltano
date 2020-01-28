import click
from . import cli
from .params import project
from contextlib import contextmanager
import itertools

from meltano.core.compiler.project_compiler import ProjectCompiler


def indent(text: str, count=2, char="  "):
    return "".join(list(itertools.repeat(char, count))) + text


@cli.group(hidden=True, invoke_without_command=True)
@project()
@click.pass_context
def model(ctx, project):
    compiler = ctx.obj["compiler"] = ProjectCompiler(project)
    compiler.parse()

    if ctx.invoked_subcommand is None:
        click.secho("Local", fg="green")
        for model in compiler.topics:
            click.echo(f'{model["namespace"]}/{model["name"]}')

        print()

        click.secho("Packaged", fg="green")
        for model in compiler.package_topics:
            click.echo(f'{model["namespace"]}/{model["name"]}')


@model.command()
@click.pass_context
def compile(ctx):
    compiler = ctx.obj["compiler"]

    compiler.compile()
    click.secho(f"Compiled {len(compiler.topics + compiler.package_topics)} model(s)")


@model.command()
@click.pass_context
def show(ctx):
    compiler = ctx.obj["compiler"]

    def print_table(table: dict):
        print(indent(table["name"], count=2))

        for dim in table.get("columns", []):
            print(indent(f"[C] {dim['name']} ({dim['sql']})", count=3))

        for dim in table.get("timeframes", []):
            print(indent(f"[T] {dim['name']} ({dim['sql']})", count=3))

        for dim in table.get("aggregates", []):
            print(indent(f"[A] {dim['name']} ({dim['sql']})", count=3))

    for model in compiler.package_topics:
        print(model["namespace"])

        for design in model["designs"]:
            print(indent(design["name"], count=1))
            print_table(design["related_table"])

            for join in design.get("joins", []):
                print_table(join["related_table"])
