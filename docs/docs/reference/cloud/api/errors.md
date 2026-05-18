---
title: Status Codes and Errors
description: Reference documentation for standard HTTP status codes and error structures returned from the Matatika API
permalink: /api/errors
parent: API
nav_order: 2
---

# {{page.title}}

The Matatika API returns standard HTTP status codes and returns an error structure explaining all failing fields.  We use a standard templated error response across different scenarios so you can expect consistency in our error responses.
{: .fs-5 }

---

In general:
- Codes in the `2xx` range indicate success
- Codes in the `4xx` range indicate an error with the request
- Codes in the `5xx` range indicate an issue with the Matatika API

Status Code | Text | Description
----------- | ---- | -----------
`200` | `OK` | The request was accepted and existing or modified data was returned.
`201` | `Created` | The request was accepted and new data was added.
`202` | `Accepted` | The request was accepted and will be processed. New data will be added once processing is complete.
`400` | `Bad Request` | The request body contained malformed content of type `application/hal+json`.
`401` | `Unauthorized` | The request does not have a valid API token.
`403` | `Forbidden` | The request has a valid API token, but is not permitted.
`404` | `Not Found` | The request URI is invalid.
`405` | `Method Not Allowed` | The request HTTP method is not supported by the endpoint.
`409` | `Conflict` | The request conflicts with current state of the server.
`503` | `Service Unavailable`| The API has encountered an error. Try again later.

---

## Validation errors - `4xx`
### Schema

Path | JSON Type | Format | Description
---- | ---- | ------ | -----------
`timestamp` | `string` | ISO 8601 timestamp | The instant when the error was encountered
`status` | `number` | HTTP status code | The error response code
`error` | `string` | | The error response text
`errors` | `object[]` | | Error object collection
`message` | `string` | | The error description
`path` | `string` | | The request path that resulted in the thrown error(s)
