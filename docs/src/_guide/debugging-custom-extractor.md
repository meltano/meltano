---
title: Debug a Custom Extractor
description: Learn how to debug a custom data extractor.
layout: doc
weight: 25
---

## Add a main block in tap.py of your Custom Extractor

```python
if __name__ == "__main__":
    # TapCustomExtractor is the class name of your tap in tap.py
    TapCustomExtractor.cli()
```

## Create a Local Venv That Your Debugger Can Use

If you're using Poetry you need to create a venv in your custom tap directory so that your IDE can pick it up when debugging.

If you have already installed poetry this will involve removing the existing poetry virtual environment. Running the command below and finally reinstalling poetry.

```bash
poetry config virtualenv.in-project true
```

## What to put in VSCode launch.json

Add the following [launch configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations) to your project:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            # Replace tap_foobar below with the actual name of your custom extractors library
            "program": "${workspaceRoot}/tap_foobar/tap.py",
            "console": "integratedTerminal",
            "args": ["--config", ".secrets/config.json"],
            "env": { "PYTHONPATH": "${workspaceRoot}"},
            # Change this to false if you wish to debug and add breakpoints outside of your code e.g. the singer-sdk package
            "justMyCode": true

        }
    ]
}

```
## Create a config.json to use when debugging

The above launch.json specifies the location of this config as ```.secrets/config.json```.

Feel free to change this but ensure the config has all the required config fields for your custom extractor to run successfully.

## Happy Debugging!

You should now be able to add breakpoints where you need and run the debugger.

## References

- [Stack Overflow: How to debug a singer tap using vs code](https://stackoverflow.com/questions/71897120/how-to-debug-a-singer-tap-using-vs-code)
