/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

const gettingStartedCategory = require('./docs/getting-started/_category_.json');

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  connectorsSidebar: [
    {
      type: 'category',
      label: 'Browse Connectors',
      link: { type: 'doc', id: 'connectors/index' },
      collapsed: false,
      items: [
        { type: 'doc', id: 'connectors/tap-apprise--matatika', label: 'Apprise ERP' },
        { type: 'doc', id: 'connectors/tap-aptean--matatika', label: 'Aptean' },
        { type: 'doc', id: 'connectors/tap-aptem--matatika', label: 'Aptem' },
        { type: 'doc', id: 'connectors/tap-auth0--matatika', label: 'Auth0' },
        { type: 'doc', id: 'connectors/tap-baidu--matatika', label: 'Baidu' },
        { type: 'doc', id: 'connectors/tap-beautifulsoup--matatika', label: 'BeautifulSoup' },
        { type: 'doc', id: 'connectors/tap-bigquery--matatika', label: 'BigQuery' },
        { type: 'doc', id: 'connectors/tap-bing-ads--matatika', label: 'Bing Ads' },
        { type: 'doc', id: 'connectors/tap-callminer--matatika', label: 'CallMiner' },
        { type: 'doc', id: 'connectors/tap-capsulecrm--matatika', label: 'Capsule' },
        { type: 'doc', id: 'connectors/tap-dbt-artifacts--matatika', label: 'dbt Artifacts' },
        { type: 'doc', id: 'connectors/tap-everflow--matatika', label: 'Everflow' },
        { type: 'doc', id: 'connectors/tap-facebook--matatika', label: 'Facebook Ads' },
        { type: 'doc', id: 'connectors/tap-facebook-systemtoken--matatika', label: 'Facebook Ads (System Access Token)' },
        { type: 'doc', id: 'connectors/tap-feefo--matatika', label: 'Feefo' },
        { type: 'doc', id: 'connectors/tap-five9--matatika', label: 'Five9' },
        { type: 'doc', id: 'connectors/tap-github--matatika', label: 'GitHub' },
        { type: 'doc', id: 'connectors/tap-googleads--matatika', label: 'Google Ads' },
        { type: 'doc', id: 'connectors/target-bigquery--matatika', label: 'Google BigQuery' },
        { type: 'doc', id: 'connectors/tap-google-sheets--matatika', label: 'Google Sheets' },
        { type: 'doc', id: 'connectors/tap-instagram--matatika', label: 'Instagram' },
        { type: 'doc', id: 'connectors/tap-instagram-system-token--matatika', label: 'Instagram (System Access Token)' },
        { type: 'doc', id: 'connectors/tap-invoca--matatika', label: 'Invoca' },
        { type: 'doc', id: 'connectors/tap-iterable--matatika', label: 'Iterable' },
        { type: 'doc', id: 'connectors/tap-linkedin-ads--matatika', label: 'LinkedIn Ads' },
        { type: 'doc', id: 'connectors/tap-matatika-sit--matatika', label: 'Matatika SIT' },
        { type: 'doc', id: 'connectors/tap-meltano--matatika', label: 'Meltano' },
        { type: 'doc', id: 'connectors/tap-msaccess--matatika', label: 'Microsoft Access' },
        { type: 'doc', id: 'connectors/tap-msaccess-anywhere--matatika', label: 'Microsoft Access Anywhere' },
        { type: 'doc', id: 'connectors/tap-msaccess-azure--matatika', label: 'Microsoft Access Azure' },
        { type: 'doc', id: 'connectors/tap-msaccess-http--matatika', label: 'Microsoft Access HTTP' },
        { type: 'doc', id: 'connectors/tap-msaccess-s3--matatika', label: 'Microsoft Access S3' },
        { type: 'doc', id: 'connectors/tap-mssql--matatika', label: 'MSSQL' },
        { type: 'doc', id: 'connectors/tap-mysql--matatika', label: 'MySQL - MariaDB' },
        { type: 'doc', id: 'connectors/tap-openweathermap--matatika', label: 'OpenWeatherMap' },
        { type: 'doc', id: 'connectors/tap-peopleware--matatika', label: 'Peopleware' },
        { type: 'doc', id: 'connectors/target-postgres--matatika', label: 'Postgres Warehouse' },
        { type: 'doc', id: 'connectors/tap-postgres--matatika', label: 'PostgreSQL' },
        { type: 'doc', id: 'connectors/tap-quickbooks--matatika', label: 'Quickbooks' },
        { type: 'doc', id: 'connectors/tap-salesforce--matatika', label: 'Salesforce' },
        { type: 'doc', id: 'connectors/tap-sharepointsites--storebrand', label: 'SharePoint' },
        { type: 'doc', id: 'connectors/tap-shopify--matatika', label: 'Shopify' },
        { type: 'doc', id: 'connectors/target-snowflake--matatika', label: 'Snowflake' },
        { type: 'doc', id: 'connectors/tap-solarvista--matatika', label: 'Solarvista Live' },
        { type: 'doc', id: 'connectors/tap-spotify--matatika', label: 'Spotify' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-anywhere--matatika', label: 'Spreadsheets Anywhere' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-azure--matatika', label: 'Spreadsheets Azure' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-gcs--matatika', label: 'Spreadsheets GCS' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-gmail--matatika', label: 'Spreadsheets Gmail' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-imap--matatika', label: 'Spreadsheets IMAP' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-outlook--matatika', label: 'Spreadsheets Outlook' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-s3--matatika', label: 'Spreadsheets S3' },
        { type: 'doc', id: 'connectors/tap-spreadsheets-sftp--matatika', label: 'Spreadsheets SFTP' },
        { type: 'doc', id: 'connectors/tap-taboola--matatika', label: 'Taboola' },
        { type: 'doc', id: 'connectors/tap-thunderboard--matatika', label: 'Thunderboard' },
        { type: 'doc', id: 'connectors/tap-tiktok--matatika', label: 'TikTok Ads' },
        { type: 'doc', id: 'connectors/tap-trello--matatika', label: 'Trello' },
        { type: 'doc', id: 'connectors/tap-govuk-bank-holidays--matatika', label: 'UK Bank Holidays' },
        { type: 'doc', id: 'connectors/tap-veeqo--matatika', label: 'Veeqo' },
        { type: 'doc', id: 'connectors/tap-govuk-weekly-road-fuel-prices--matatika', label: 'Weekly road fuel prices' },
        { type: 'doc', id: 'connectors/tap-xero--matatika', label: 'Xero' },
      ],
    },
  ],
  platformSidebar: [
    {
      type: 'category',
      label: 'Getting Started',
      customProps: gettingStartedCategory.customProps,
      link: { type: 'doc', id: 'getting-started/which-meltano' },
      items: [
        {
          type: 'doc',
          id: 'getting-started/which-meltano',
          label: 'Which Meltano is right for you?',
        },
      ],
    },
    {
      type: 'category',
      label: require('./docs/meltano-cloud/_category_.json').label,
      customProps: require('./docs/meltano-cloud/_category_.json').customProps,
      link: { type: 'doc', id: 'meltano-cloud/index' },
      collapsed: true,
      items: [
        { type: 'doc', id: 'meltano-cloud/cloud-overview' },
        { type: 'doc', id: 'meltano-cloud/creating-workspace' },
        { type: 'doc', id: 'meltano-cloud/managing-a-workspace' },
        {
          type: 'category',
          label: 'Connect a store',
          link: { type: 'doc', id: 'meltano-cloud/connect-a-store/index' },
          items: [
            { type: 'doc', id: 'meltano-cloud/connect-a-store/snowflake-guides' },
            { type: 'doc', id: 'meltano-cloud/connect-a-store/microsoft-sql-server-guides' },
            //{ type: 'doc', id: 'meltano-cloud/stores/bigquery' },
          ],
        },
        { type: 'doc', id: 'meltano-cloud/setup-development-environment' },
        { type: 'doc', id: 'meltano-cloud/automate-actions' },
        { type: 'doc', id: 'meltano-cloud/plugins' },
        { type: 'doc', id: 'meltano-cloud/importing-data' },
        { type: 'doc', id: 'meltano-cloud/transform-data' },
        { type: 'doc', id: 'meltano-cloud/workspace-settings' },
        { type: 'doc', id: 'meltano-cloud/logging-monitoring' },
        { type: 'doc', id: 'meltano-cloud/profile-security' },
        { type: 'doc', id: 'meltano-cloud/invite' },
        //{ type: 'doc', id: 'meltano-cloud/snowflake-guides' },
      ],
    },

    {
      type: 'category',
      label: require('./docs/meltano-open/_category_.json').label,
      customProps: require('./docs/meltano-open/_category_.json').customProps,
      link: { type: 'doc', id: 'meltano-open/index' },
      collapsed: true,
      items: [
        {
          type: 'doc',
          id: 'meltano-open/meltano-at-a-glance',
          label: 'Overview',
        },
        {
          type: 'doc',
          id: 'meltano-open/installation',
          label: 'Self-host install',
        },
        { type: 'doc', id: 'guide/installation-guide' },
        { type: 'doc', id: 'guide/plugin-management' },
        { type: 'doc', id: 'guide/configuration' },
        { type: 'doc', id: 'guide/integration' },
        { type: 'doc', id: 'guide/complete_tutorial' },
        { type: 'doc', id: 'guide/mappers' },
        { type: 'doc', id: 'guide/transformation' },
        { type: 'doc', id: 'guide/orchestration' },
        { type: 'doc', id: 'guide/analysis' },
        { type: 'doc', id: 'guide/containerization' },
        { type: 'doc', id: 'guide/production' },
        { type: 'doc', id: 'guide/advanced-topics' },
        { type: 'doc', id: 'guide/logging' },
        { type: 'doc', id: 'guide/v2-migration' },
        { type: 'doc', id: 'guide/v3-migration' },
        { type: 'doc', id: 'guide/v4-migration' },
        { type: 'doc', id: 'guide/debugging-custom-extractor' },
        { type: 'doc', id: 'guide/custom-state-backend' },
        { type: 'doc', id: 'guide/migrate-an-existing-dbt-project' },
        { type: 'doc', id: 'guide/user-yaml-config' },
        { type: 'doc', id: 'guide/troubleshooting' },
      ],
    },
    {
      type: 'category',
      label: require('./docs/concepts/_category_.json').label,
      customProps: require('./docs/concepts/_category_.json').customProps,
      link: { type: 'doc', id: 'concepts/index' },
      items: [{ type: 'autogenerated', dirName: 'concepts' }],
    },
    {
      type: 'category',
      label: require('./docs/reference/_category_.json').label,
      customProps: require('./docs/reference/_category_.json').customProps,
      link: { type: 'doc', id: 'reference/index' },
      items: [{ type: 'autogenerated', dirName: 'reference' }],
    },
    {
      type: 'category',
      label: require('./docs/tutorials/_category_.json').label,
      customProps: require('./docs/tutorials/_category_.json').customProps,
      link: { type: 'doc', id: 'tutorials/index' },
      items: [{ type: 'autogenerated', dirName: 'tutorials' }],
    },
    {
      type: 'category',
      label: require('./docs/contribute/_category_.json').label,
      customProps: require('./docs/contribute/_category_.json').customProps,
      link: { type: 'doc', id: 'contribute/index' },
      items: [{ type: 'autogenerated', dirName: 'contribute' }],
    },
  ],
};


module.exports = sidebars;
