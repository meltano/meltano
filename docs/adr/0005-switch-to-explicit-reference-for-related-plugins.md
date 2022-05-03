# 5. Switch to a explicit reference for related plugins

Date: 2022-05-03

## Status

Proposed

## Context

Previously, when a user added certain plugins, any related plugin such as a file bundle would be added as well.
This dependency was based on the name / namespace of the plugin.

As part of Meltano 2.0 we aim to make this dependency more explicit to provide the user with more control when adding and installing plugins. 

## Decision

We will add an explicit reference in the definiton of a plugin to other plugins using the `related_plugin` key. 

The ability to auto-add and install plugins based on the similarity of the name and/or namespace will be deprecated.

References to plugins will initially be in the form of a URL reference to a full plugin definition. 
Future iterations will allow for versioning, variant specification, and possibly requirement rules. 

## Consequences

Referenced / bundled plugins will be installed as a top-level plugin entry during `meltano add`. 
