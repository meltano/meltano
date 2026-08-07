import React, { useState } from 'react';

const CONNECTORS = [
  { label: 'Apprise ERP', href: '/connectors/tap-apprise--matatika' },
  { label: 'Aptean', href: '/connectors/tap-aptean--matatika' },
  { label: 'Aptem', href: '/connectors/tap-aptem--matatika' },
  { label: 'Auth0', href: '/connectors/tap-auth0--matatika' },
  { label: 'Baidu', href: '/connectors/tap-baidu--matatika' },
  { label: 'BeautifulSoup', href: '/connectors/tap-beautifulsoup--matatika' },
  { label: 'BigQuery', href: '/connectors/tap-bigquery--matatika' },
  { label: 'Bing Ads', href: '/connectors/tap-bing-ads--matatika' },
  { label: 'CallMiner', href: '/connectors/tap-callminer--matatika' },
  { label: 'Capsule', href: '/connectors/tap-capsulecrm--matatika' },
  { label: 'dbt Artifacts', href: '/connectors/tap-dbt-artifacts--matatika' },
  { label: 'Everflow', href: '/connectors/tap-everflow--matatika' },
  { label: 'Facebook Ads', href: '/connectors/tap-facebook--matatika' },
  { label: 'Facebook Ads (System Access Token)', href: '/connectors/tap-facebook-systemtoken--matatika' },
  { label: 'Feefo', href: '/connectors/tap-feefo--matatika' },
  { label: 'Five9', href: '/connectors/tap-five9--matatika' },
  { label: 'GitHub', href: '/connectors/tap-github--matatika' },
  { label: 'Google Ads', href: '/connectors/tap-googleads--matatika' },
  { label: 'Google BigQuery', href: '/connectors/target-bigquery--matatika' },
  { label: 'Google Sheets', href: '/connectors/tap-google-sheets--matatika' },
  { label: 'Instagram', href: '/connectors/tap-instagram--matatika' },
  { label: 'Instagram (System Access Token)', href: '/connectors/tap-instagram-system-token--matatika' },
  { label: 'Invoca', href: '/connectors/tap-invoca--matatika' },
  { label: 'Iterable', href: '/connectors/tap-iterable--matatika' },
  { label: 'LinkedIn Ads', href: '/connectors/tap-linkedin-ads--matatika' },
  { label: 'Matatika SIT', href: '/connectors/tap-matatika-sit--matatika' },
  { label: 'Meltano', href: '/connectors/tap-meltano--matatika' },
  { label: 'Microsoft Access', href: '/connectors/tap-msaccess--matatika' },
  { label: 'Microsoft Access Anywhere', href: '/connectors/tap-msaccess-anywhere--matatika' },
  { label: 'Microsoft Access Azure', href: '/connectors/tap-msaccess-azure--matatika' },
  { label: 'Microsoft Access HTTP', href: '/connectors/tap-msaccess-http--matatika' },
  { label: 'Microsoft Access S3', href: '/connectors/tap-msaccess-s3--matatika' },
  { label: 'MSSQL', href: '/connectors/tap-mssql--matatika' },
  { label: 'MySQL - MariaDB', href: '/connectors/tap-mysql--matatika' },
  { label: 'OpenWeatherMap', href: '/connectors/tap-openweathermap--matatika' },
  { label: 'Peopleware', href: '/connectors/tap-peopleware--matatika' },
  { label: 'Postgres Warehouse', href: '/connectors/target-postgres--matatika' },
  { label: 'PostgreSQL', href: '/connectors/tap-postgres--matatika' },
  { label: 'Quickbooks', href: '/connectors/tap-quickbooks--matatika' },
  { label: 'Salesforce', href: '/connectors/tap-salesforce--matatika' },
  { label: 'SharePoint', href: '/connectors/tap-sharepointsites--storebrand' },
  { label: 'Shopify', href: '/connectors/tap-shopify--matatika' },
  { label: 'Snowflake', href: '/connectors/target-snowflake--matatika' },
  { label: 'Solarvista Live', href: '/connectors/tap-solarvista--matatika' },
  { label: 'Spotify', href: '/connectors/tap-spotify--matatika' },
  { label: 'Spreadsheets Anywhere', href: '/connectors/tap-spreadsheets-anywhere--matatika' },
  { label: 'Spreadsheets Azure', href: '/connectors/tap-spreadsheets-azure--matatika' },
  { label: 'Spreadsheets GCS', href: '/connectors/tap-spreadsheets-gcs--matatika' },
  { label: 'Spreadsheets Gmail', href: '/connectors/tap-spreadsheets-gmail--matatika' },
  { label: 'Spreadsheets IMAP', href: '/connectors/tap-spreadsheets-imap--matatika' },
  { label: 'Spreadsheets Outlook', href: '/connectors/tap-spreadsheets-outlook--matatika' },
  { label: 'Spreadsheets S3', href: '/connectors/tap-spreadsheets-s3--matatika' },
  { label: 'Spreadsheets SFTP', href: '/connectors/tap-spreadsheets-sftp--matatika' },
  { label: 'Taboola', href: '/connectors/tap-taboola--matatika' },
  { label: 'Thunderboard', href: '/connectors/tap-thunderboard--matatika' },
  { label: 'TikTok Ads', href: '/connectors/tap-tiktok--matatika' },
  { label: 'Trello', href: '/connectors/tap-trello--matatika' },
  { label: 'UK Bank Holidays', href: '/connectors/tap-govuk-bank-holidays--matatika' },
  { label: 'Veeqo', href: '/connectors/tap-veeqo--matatika' },
  { label: 'Weekly road fuel prices', href: '/connectors/tap-govuk-weekly-road-fuel-prices--matatika' },
  { label: 'Xero', href: '/connectors/tap-xero--matatika' },
];

export default function ConnectorSearch() {
  const [query, setQuery] = useState('');

  const filtered = query.trim()
    ? CONNECTORS.filter(c => c.label.toLowerCase().includes(query.toLowerCase()))
    : CONNECTORS;

  return (
    <>
      <div className="connector-search-wrapper">
        <input
          className="connector-search-input"
          type="search"
          placeholder="Search connectors…"
          value={query}
          onChange={e => setQuery(e.target.value)}
          aria-label="Search connectors"
        />
      </div>

      {filtered.length === 0 ? (
        <p className="connector-search-empty">No connectors match "<strong>{query}</strong>".</p>
      ) : (
        <div className="connector-search-results connectors-grid">
          {filtered.map(c => (
            <a key={c.href} className="connector-card" href={c.href}>
              {c.label}
            </a>
          ))}
        </div>
      )}
    </>
  );
}
