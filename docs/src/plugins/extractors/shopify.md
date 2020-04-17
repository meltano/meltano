---
sidebar: auto
metaTitle: Extract Data from Shopify
description: Use Meltano to extract raw data from Shopify and insert it into Postgres, Snowflake, and more.
---

# Shopify

The Shopify extractor pulls raw data from the [Shopify API](https://shopify.dev/docs/admin-api/rest/reference) and extracts the following resources from a Shopify shop:

- [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
- [Collects](https://help.shopify.com/en/api/reference/products/collect)
- [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
- [Customers](https://help.shopify.com/en/api/reference/customers)
- [Metafields](https://help.shopify.com/en/api/reference/metafield)
- [Orders](https://help.shopify.com/en/api/reference/orders)
- [Products](https://help.shopify.com/en/api/reference/products)
- [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)

For more information you can check [the documentation for tap-shopify](https://github.com/singer-io/tap-shopify).

## Shopify Setup

In order to access your Shopify data, you will need:

- Store Subdomain
- Private App API Password
- Start Date

<h3 id="shop">Store Subdomain</h3>

The store subdomain can be derived from your Shopify admin URL.

If your admin URL starts with `https://my-first-store.myshopify.com/`, your store subdomain is `my-first-store`.

<h3 id="api-key">Private App API Password</h3>

#### Create private app

First, you will need to create a [Private App](https://help.shopify.com/en/manual/apps/private-apps):

1. Log in to your Shopify store admin at `https://<store subdomain>.myshopify.com/admin`
2. Click "Apps" in the sidebar on the left
3. On the bottom of the page, click "Manage private apps" next to "Working with a developer on your shop?"
4. Click the "Create a new private app" button
5. Enter a "Private app name" of your choosing, e.g. "Meltano"
6. Enter your email address under "Emergency developer email"
7. In the "Admin API" section, click "▼ Review disabled Admin API permissions"
8. Choose "Read access" rather than "No access" in the access level dropdowns for the following permissions:
   1. Products, variants and collections - `read_products, write_products`
   2. Orders, transactions and fulfillments - `read_orders, write_orders`
   3. Customer details and customer groups - `read_customers, write_customers`
9. Click "Save"
10. In the modal that appears, click "I understand, create the app"

#### Find your API password

Now that your app has been created, we can acquire the password Meltano will use to authenticate with the Shopify API.

1. In the "Admin API" section on the private app details page, find the "Password" field and click "Show"
2. The value that appears (starting with `shppa_`) is your API password. You can copy and paste it into the Meltano data source configuration.

![Screenshot of Shopify interface showing private app API password](/images/tap-shopify/private-app-api-password.png)

### Start Date

This property determines how much historical data will be extracted.

Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.

## Advanced: Command Line Installation

1. Navigate to your Meltano project in the terminal
2. Run the following command:

```bash
meltano add extractor tap-shopify
```

If you are successful, you should see `Added and installed extractors 'tap-shopify'` in your terminal.

### Configuration

1. Open your project's `.env` file in a text editor
1. Add the following variables to your file:

```bash
# See above for steps on how to acquire "Store Subdomain"
export TAP_SHOPIFY_SHOP="my-first-store"
# See above for steps on how to acquire "Private App API Password"
export TAP_SHOPIFY_API_KEY="shppa_1a2b3c4d5e6f"
# The date uses ISO-8601 and supports time if desired
export TAP_STRIPE_START_DATE="YYYY-MM-DD"
```

## Additional Information

- **Data Source**: [Shopify's API](https://shopify.dev/docs/admin-api/rest/reference)
- **Repository**: <https://github.com/singer-io/tap-shopify>
