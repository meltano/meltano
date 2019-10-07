---
sidebar: auto
---

# Stripe

`tap-stripe` is an extractor that pulls data from Stripe's API and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## Info

- **Data Source**: [Stripe's API](https://stripe.com/docs/api)
- **Repository**: [https://github.com/meltano/tap-stripe](https://github.com/meltano/tap-stripe)

## Install

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-stripe
```

If you are successful, you should see `Added and installed extractors 'tap-stripe'` in your terminal.

## Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
export STRIPE_API_KEY="yourStripeApiKey"
# The date uses ISO-8601 and supports time if desired
export TAP_STRIPE_START_DATE="YYYY-MM-DD"
```
