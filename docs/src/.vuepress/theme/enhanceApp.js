export default ({
  Vue, // the version of Vue being used in the VuePress app
  options, // the options for the root Vue instance
  router, // the router instance for the app
  siteData, // site metadata,
  isServer // is this enhancement applied in server-rendering or client
}) => {
  if (!isServer) {
    window.addEventListener('load', enableExternalScroll);
  }

  function enableExternalScroll() {
    window.addEventListener('message', msg => {
      if (msg.data['source'] == 'meltano') {
        const anchor_name = msg.data['anchor'];
        const anchor = document.getElementById(anchor_name);

        if (anchor) {
          anchor.scrollIntoView();
        }
      }
    });
  }
    
    router.addRoutes([
        { path: '/plugins/extractors/bigquery.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/bing.html-ads', redirect: '/docs/hub' },
        { path: '/plugins/extractors/chargebee.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/csv.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/facebook.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/fastly.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/gitlab.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/adwords.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/google.html-analytics', redirect: '/docs/hub' },
        { path: '/plugins/extractors/marketo.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/mongodb.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/mysql.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/postgres.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/quickbooks.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/recharge.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/intacct.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/salesforce.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/shopify.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/slack.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/spreadsheets.html-anywhere', redirect: '/docs/hub' },
        { path: '/plugins/extractors/stripe.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/zendesk.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/zendesk--singer-io.html', redirect: '/docs/hub' },
        { path: '/plugins/extractors/zoom.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/bigquery.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/csv.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/jsonl.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/postgres.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/postgres--meltano.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/postgres--transferwise.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/redshift.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/snowflake.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/snowflake--meltano.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/snowflake--transferwise.html', redirect: '/docs/hub' },
        { path: '/plugins/loaders/sqlite.html', redirect: '/docs/hub' }
    ])
};

