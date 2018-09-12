# API Dockerfile Build

The api requires both python and node. We want to use the upstream python and
node dockerfiles because result in smaller images and they get lots of
bugfixes. Dockerfiles built with from stackoverflow "how do I install python"
are bound to become unpredictable.

## build_dockerfile.py

[`build_dockerfile.py api/build/Dockerfile.template`](../../bin/build_dockerfile.py) does
the following:

- reads lines in [build/Dockerfile.template](base/Dockerfile.template) to stdout
- for every `# @include FILE` directive a processed version of `FILE` to stdout:
  - [build/python.Dockerfile](vendor/python/Dockerfile)
  - [build/node.Dockerfile](vendor/node/Dockerfile)
  
Run `make api/Dockerfile` to automate the above

You will only ever need to do this if:

- [Dockerfile.template]() is updated
- [python.Dockerfile]() or [node.Dockerfile]() are updated
- [build_dockerfile.py]() is updated

`make api/Dockerfile` is idempotent and only rebuilds the Dockerfile if changes to the above files have been made

## how to update the upstream Node and Python dockerfiles

Just delete them and run either `make api/Dockerfile` or `make api/build/node.Dockerfile` for instance.


