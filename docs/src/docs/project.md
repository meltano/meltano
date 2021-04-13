---
description: At the core of the Meltano experience is your Meltano project, which represents the single source of truth regarding your ELT pipelines.
---

# Meltano Project

At the core of the Meltano expirience is the Meltano project.
This project is defined in a text-based file format and represents the 
state of your entire data stack. Everything from data extraction, loading,
transformation, orchestration, and more. 

Since a Meltano project is a directory on your filesystem with 
text-based files, you can treat it like any other software development project
and benefit from DataOps best practices such as version control, code review,
and continuous integration and deployment (CI/CD).

## Why files?

Development, whether for software engineers or data professionals, is
about working at a meaningful level of abstraction. We believe that defining
configuration in YAML-based text files is a valuabe pattern that is repeated
many times within software development. YAML is a convenient interface for 
humans to create definitions that computers can also read. 

Once you have this interface, you can define the level of abstraction to
implement. With Meltano, we aim to be the system that enables easy configuration 
and management of many different `plugins` which can be swapped in and out
depending on the use case. 

## `meltano.yml` project file

A Meltano project will always contain a project file named `meltano.yml`.
This contains your project configuration and tells Meltano that a particular directory is a Meltano project.
