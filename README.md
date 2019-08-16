[![pipeline status](https://gitlab.com/meltano/meltano/badges/master/pipeline.svg)](https://gitlab.com/meltano/meltano/commits/master)

# Meltano

Meltano [(www.meltano.com)](https://meltano.com/) is an open source convention-over-configuration product for the whole data lifecycle, all the way from loading data to analyzing it.

It does [data ops](https://en.wikipedia.org/wiki/DataOps), data engineering, analytics, business intelligence, and data science. It leverages open source software and software development best practices including version control, CI, CD, and review apps.

Meltano stands for the [steps of the data science life-cycle](#data-science-lifecycle): Model, Extract, Load, Transform, Analyze, Notebook, and Orchestrate.

## Documentation

You can find our documentation at [https://www.meltano.com/docs/](https://www.meltano.com/docs/).

For more information on the source code for the docs and running it locally, you can find them in the [docs directory on this project](https://gitlab.com/meltano/meltano/tree/master/docs).

## Contributing to Meltano

We welcome contributions and improvements, please see the [contribution guidelines](https://meltano.com/docs/contributing.html)

### Metrics Preferences

As you contribute to Meltano, you may want to disable metrics tracking globally rather than by project. To do this, you can do this by setting the environment variable `MELTANO_DISABLE_TRACKING=True`.

#### bash

1. Open your terminal
2. Edit `~/.bashrc` with a text editor
3. Add the following lines:

```bash
# Disable tracking across all Meltano projects
export MELTANO_DISABLE_TRACKING=True
```

4. Restart your terminal
5. Run `echo $MELTANO_DISABLE_TRACKING` and you should receive `True` as your output

#### Zsh

1. Open your terminal
2. Edit `~/.zshrc` with a text editor
3. Add the following lines:

```bash
# Disable tracking across all Meltano projects
export MELTANO_DISABLE_TRACKING=True
```

4. Restart your terminal
5. Run `echo $MELTANO_DISABLE_TRACKING` and you should receive `True` as your output

## License

This code is distributed under the MIT license, see the [LICENSE](LICENSE) file.

[docker-compose]: https://docs.docker.com/compose/
