# 2. Snowplow events will be initially implemented to achieve parity with Google Analytics

Date: 2022-02-24

## Status

Proposed

## Context

We are aiming to move away from Google Anlaytics event tracking and towards Snowplow so that we can 
improve and increase the kind of data we're receiving from users. 
This work is tracked in [this epic](https://gitlab.com/groups/meltano/-/epics/122). 

Part of the value of Snowplow is the ability to define schemas for events therby enabling a overall
better structure and understanding of event meaning for downstream analytics use cases.

## Decision

As a first iteration to gain parity between Google Anlaytics and Snowplow, we will implement a dual-reporting
event structure and send identical events to both services. 

## Consequences

This decision does not yet take full advantage of Snowplow metadata features.
This is done to get the end-to-end snowplow pipelines flowing and reporting switched from GA to Snowplow.

We will go forward after this is in place to refactor all of the event reporting to get better structure overall.
