# Meltano Plugins With Custom Python Versions

An overview of how Meltano plugins can use different Python versions in their virtual environments than the Python version used to run Meltano itself.

Here we'll add the extractor `tap-github` using the Python executable `python3.X`. Since we've provided the name of an executable, rather than a file path, it will be found on `$PATH`.

For the sake of this example, to avoid requiring a second or third Python installation, we'll copy the Python executable to new names `python3.X` and `python3.Y` that can be found on our `$PATH`. Later this will let us distinguish it from the one that would be used by default.

```shell
PATH="$PWD:$PATH"
cp "$(python -c 'import os, sys; print(os.path.realpath(sys.executable))')" ./python3.X
cp "$(python -c 'import os, sys; print(os.path.realpath(sys.executable))')" ./python3.Y
chmod u+x ./python3.X ./python3.Y
```

In practice you'll want to use a particular version of Python that has already been installed such as `python3.12`.

When this value isn't provided, Meltano will use the Python executable that was used to run Meltano itself.

In `meltano.yml` we have set the `python` property to `python3.X`, which will be used instead of the Python executable that was used to run Meltano itself.

```shell
meltano add tap-github
```

In this case since we've used `python3.X`, we'll find that when we run the plugin's version of Python, it will use the `python3.X` executable.

```shell
.meltano/extractors/tap-github/venv/bin/python -c 'import os, sys; exe = os.path.realpath(sys.executable); print(exe); exit(not exe.endswith("/python3.X"))'
```

Now we can add a different plugin that specifies the Python version it should use at the plugin level:

```shell
meltano add tap-gitlab --python python3.Y
```

And then test that it uses the Python executable we expect, `python3.Y`, instead of `python3.X` or the Python version that was used to run Meltano:

```shell
.meltano/extractors/tap-gitlab/venv/bin/python -c 'import os, sys; exe = os.path.realpath(sys.executable); print(exe); exit(not exe.endswith("/python3.Y"))'
```

### Cleanup

```shell
rm ./python3.X ./python3.Y
```
