---
title: API Development
description: Contribute to the Meltano API.
layout: doc
weight: 10
---

This section of the guide provides guidance on how to work with the Meltano API, which serves as the backend of Meltano and is built with the [Python framework: Flask](https://github.com/pallets/flask).

## Getting Set Up

After all of your dependencies installed, we recommend opening a new window/tab in your terminal so you can run the following commands:

```bash
# Create a new Meltano project
meltano init $PROJECT_NAME

# Change directory into your newly created project
cd $PROJECT_NAME

# Start a development build of the Meltano API and a production build of Meltano UI
FLASK_ENV=development meltano ui
```

The development build of the Meltano API and a production build of the UI will now be available at <http://localhost:5000/>.

<div class="notification is-danger">
  <p><strong>Potential MacOS port conflicts</strong></p>
  <p>On recent versions of MacOS (Monterey/12.0 and up) an AirPlay related service may be bound to port 5000. In that scenario you may want to specify an alternate <a href="/reference/settings#ui-bind-port">bind to port</a> to start the service on a port other than 5000. If you would like to continue using that port, please consult this <a href="https://developer.apple.com/forums/thread/682332">Apple Developers Forum article</a> to how to reset port 5000.</p>
</div>

## Debugging Your Code

Here is the recommended way to validate / debug your code:

```
# Purpose: Start a debugger
# Usage: Use as a one-line import / invocation for easier cleanup
import pdb;
pdb.set_trace()
```
