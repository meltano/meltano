#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
from os.path import abspath, dirname, join, commonpath, relpath, basename
from shutil import copyfile
from typing import TextIO


def include_dockerfile(dockerfile_path: str, out: TextIO):
    with open(abspath(dockerfile_path)) as df:
        content_start = False
        for line in df:
            # strip directives we don't like
            if line.lower().startswith(('#', 'from', 'cmd')):
                continue
            # trim beginning whitespace
            if not content_start and not line.strip():
                continue
            content_start = True
            out.write(line)


def build_dockerfile(template_file: TextIO, out_file: TextIO = None):
    if out_file:
        out_dest = out_file
        friendly_template_path = relpath(template_file.name, dirname(out_file.name))
    else:
        out_dest = sys.stdout
        friendly_template_path = basename(template_file.name)


    def out(x):
        print(x, file=out_dest)

    out('''
#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "bin/build_dockerfile.py"
#
# PLEASE DO NOT EDIT IT DIRECTLY. EDIT "{}" INSTEAD
#
    '''.strip().format(friendly_template_path))
    for line in template_file:
        if line.startswith('# @include'):
            include_file_arg = line.split()[2].strip()
            if not include_file_arg:
                continue

            include_file = abspath(join(dirname(template_file.name), include_file_arg))

            if out_file:
                include_file_rel = relpath(include_file, dirname(out_file.name))
            else:
                include_file_rel = include_file_arg
            out(line.replace(include_file_arg, include_file_rel).strip())

            include_dockerfile(include_file, out_dest)
            out(f'# @endinclude {include_file_rel}')

            continue
        out(line.strip())


if __name__ == '__main__':

    parser = ArgumentParser(description='Build a Dockerfile from a template.')
    parser.add_argument('template_file', type=str, help='template file path')
    parser.add_argument('-o', type=str, dest='out_file', default='-',
                        help='output file path. use `-` for stdout (default)')

    args = parser.parse_args()

    with open(abspath(args.template_file), 'r') as template:
        if args.out_file == '-':
            build_dockerfile(template)
            exit(0)

        out_file_arg = abspath(args.out_file)
        swap_file = open(f'{out_file_arg}.swp', 'w+')
        try:
            build_dockerfile(template, swap_file)
            swap_file.close()
            copyfile(swap_file.name, out_file_arg)
        finally:
            swap_file.close()
            os.remove(swap_file.name)
