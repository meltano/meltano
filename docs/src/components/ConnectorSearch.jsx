import React, { useState } from 'react';

const CONNECTORS = [
  { label: 'Outlook', href: '/connectors/tap-spreadsheets-outlook' },
  { label: 'SharePoint', href: '/connectors/tap-spreadsheets-sharepoint' },
];

export default function ConnectorSearch() {
  const [query, setQuery] = useState('');

  const q = query.trim().toLowerCase();
  const filtered = q
    ? CONNECTORS.filter(c => c.label.toLowerCase().includes(q))
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
