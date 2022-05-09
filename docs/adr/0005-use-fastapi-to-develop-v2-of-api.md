# 5. Use FastAPI to develop v2 of API

Date: 2022-05-09

## Status

Accepted

## Context

Version 1 of the Meltano API is a bit inconsistent both in API design and implementation.  Critically, it lacks full feature parity with the CLI, and there are features and patterns that are not completely implemented, have little support knowledge, or are generally features we'd prefer to deprecate (dashboards, models, etc.). 

Lastly, the API is implemented using Gunicorn + Flask, which while time tested has some issues. Gunicorn lacks Windows support, Flask is a WSGI app with no first class asyncio support. 

The goals of a v2 API and ultimately the requirements for a future framework would be to:

- Cohesively organized resource API endpoints.
- Standardized endpoint structure and naming conventions.
- Create a clean implementation free of "special sauce" that leverage's meltano.core as a lib as much as possible.
- Support async out of the box, with the ability to integrate job/task queue's if required.
- Low barrier to entry for dev iteration and contributors. We should be able to rapidly and incrementally ship this new version (weeks, not months).
- Support common client languages with auto-generated client libs and auto-documented endpoints. (no half finished empty swagger docs).
- Ability to achieve CLI parity if desired, again, requiring no special sauce.
- Relatively future-proof. Adding new endpoints and features should be straightforward and not break the API design. Only a major reorganization of the collections/resources of the API should require a v3.

With those topics in mind, we investigated what technology we might build on for v2 of the API and how to bring the rest API to parity with the meltano CLI. The result of this investigation was [#3302](https://gitlab.com/meltano/meltano/-/issues/3302) which among a few topics also includes an investigation and evaluation of a Python GRPC based v2 implementation, and a FastAPI based implementation. 

## Decision

Version 2 of the meltano API will be built using FastAPI.

- FastAPI has board community adoption, more so than GRPC
- FastAPI can be OpenAPI compliant and its "just python" so very approachable.
- The overall developer experience for our contributor base will be very robust and the barrier to contribution will be quite low. FastAPI is also simple enough that even developers without prior exposure to it should find it easy to pick up and onboard to both FastAPI and our particular pattern of usage.
- GRPC would require contributors to become familiar with protobuf for service and message definitions.
- GRPC isn't as easy to interact with as a vanilla HTTP API.
- Asyncio is supported out of the box.
- The default ASGI worker server Uvicorn has Windows support in addition to Linux/Mac.
- FastAPI supports exposing/mounting WSGI apps, which will likely allow for a simpler way to run both the v1 and v2 API for a period of time.

FastAPI can support streaming responses (which we will likely require for streaming logs), however, being HTTP-based the usual caveats apply. Namely, streaming responses in v2 of our API will require implementing streaming ND-JSON, FastAPI's websockets implementation, or a Server-Sent Events implementation (perhaps using a plugin like sse-starlette).

While we've not officially made a streaming response decision as part of this ADR, we will bias towards a streaming nd-json. While we acknowledge streaming nd-json is kludge on HTTP1, it's a common one and likely easier to deal with than Websockets, particularly since it's unlikely that we'll require bidirectional streaming or client request streaming.

## Consequences

No new features will be introduced in the v1 API, and it will effectively enter a maintenance only mode (the UI will likely continue to receive quality of life improvements backed by the v1 API for a period of time).

A minimal FastAPI skeleton mounting and exposing the v1 API will be created. As part of this, we'll likely replace Gunicorn with Uvicorn, which should also allow Windows users to begin running the API natively.

The UI will continue to use and leverage and the v1, but a future ADR will be logged when a decision is made on how the UI will leverage the v2 API.

Lastly, it's important to note that while FastAPI can be OpenAPI compliant. Diligence is required to yield a spec/client with a pleasant UX (curating tags, custom op IDs and name generators, etc.), and since the service spec isn't strictly speaking a spec but just your endpoints as written in code, there's more room for drift in project standards and endpoint consistency. Detailed contributor guidance, diligent code reviews, and careful grooming of doc strings will be key.
