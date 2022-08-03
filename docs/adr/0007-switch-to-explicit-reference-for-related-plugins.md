# 7. Switch to a explicit reference for related plugins

Date: 2022-05-17

## Status

Accepted

## Context

Previously, when a user added certain plugins, any related plugin such as a file bundle would be added as well.
This dependency was based on the name / namespace of the plugin.

As part of Meltano 2.0 we aim to make this dependency explicit to provide the user with more control when adding and installing plugins. 

## Decision

Within the definition of a plugin, we will add a new top-level key to specify required plugin dependencies.

This is a complete replacement of the current behavior to auto-add and install plugins based on the similarity of the name and/or namespace.

References to plugins will initially be in the form of a URL reference to a full plugin definition. 
Future iterations will allow for versioning, variant specification, and possibly requirement rules. 

## Consequences

Referenced / bundled plugins will be installed as a top-level plugin entry during `meltano add`. 
