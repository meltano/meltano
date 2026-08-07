import React, { useState, useRef, useEffect } from 'react';
import { ArrowLineRight, Database } from '@phosphor-icons/react/ssr';
import ConnectorTypeBadge from './ConnectorTypeBadge';

const CONNECTORS = [
  { label: 'Spreadsheets (Outlook)', href: '/connectors/tap-spreadsheets-outlook', category: 'extractor' },
  { label: 'Spreadsheets (SharePoint)', href: '/connectors/tap-spreadsheets-sharepoint', category: 'extractor' },
  { label: 'Zendesk', href: '/connectors/tap-zendesk', category: 'extractor' },
  { label: 'SurveyMonkey', href: '/connectors/tap-surveymonkey', category: 'extractor' },
  { label: 'Rakuten Advertising', href: '/connectors/tap-rakutenadvertising', category: 'extractor' },
  { label: 'Spreadsheets (IMAP)', href: '/connectors/tap-spreadsheets-imap', category: 'extractor' },
  { label: 'Weather API', href: '/connectors/tap-weatherapi', category: 'extractor' },
  { label: 'ClickHouse', href: '/connectors/target-clickhouse', category: 'loader' },
];

function ConnectorCardTitle({ label }) {
  const textRef = useRef(null);
  const [overflowing, setOverflowing] = useState(false);

  useEffect(() => {
    const el = textRef.current;
    if (el) {
      setOverflowing(el.scrollWidth > el.clientWidth + 1);
    }
  }, [label]);

  return (
    <span className="connector-card-title">
      <span
        className={`connector-card-title-track${overflowing ? ' connector-card-title-track--overflowing' : ''}`}
      >
        <span className="connector-card-title-text" ref={textRef}>{label}</span>
        {overflowing && (
          <span className="connector-card-title-text" aria-hidden="true">{label}</span>
        )}
      </span>
    </span>
  );
}

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'extractor', label: 'Extractor', Icon: ArrowLineRight },
  { key: 'loader', label: 'Loader', Icon: Database },
];

export default function ConnectorSearch() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('all');

  const q = query.trim().toLowerCase();
  const filtered = CONNECTORS.filter((c) => {
    const matchesQuery = q ? c.label.toLowerCase().includes(q) : true;
    const matchesCategory = category === 'all' ? true : c.category === category;
    return matchesQuery && matchesCategory;
  }).sort((a, b) => a.label.localeCompare(b.label));

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

      <div className="connector-filter-bar" role="group" aria-label="Filter connectors by type">
        {FILTERS.map(({ key, label, Icon }) => (
          <button
            key={key}
            type="button"
            className={`connector-filter-chip connector-filter-chip--${key}${category === key ? ' connector-filter-chip--active' : ''}`}
            aria-pressed={category === key}
            onClick={() => setCategory(key)}
          >
            {Icon && <Icon size={16} weight="light" />}
            {label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <p className="connector-search-empty">No connectors match "<strong>{query}</strong>".</p>
      ) : (
        <div className="connector-search-results connectors-grid">
          {filtered.map(c => (
            <a key={c.href} className="connector-card" href={c.href}>
              <ConnectorCardTitle label={c.label} />
              <ConnectorTypeBadge type={c.category} />
            </a>
          ))}
        </div>
      )}
    </>
  );
}
