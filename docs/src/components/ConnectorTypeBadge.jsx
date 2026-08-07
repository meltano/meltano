import React from 'react';
import { ArrowLineRight, Database } from '@phosphor-icons/react/ssr';

const CATEGORY_META = {
  extractor: { label: 'Extractor', Icon: ArrowLineRight },
  loader: { label: 'Loader', Icon: Database },
};

export default function ConnectorTypeBadge({ type, block }) {
  const { label, Icon } = CATEGORY_META[type];
  const badge = (
    <span className={`connector-card-badge connector-card-badge--${type}`}>
      <Icon size={12} weight="light" />
      {label}
    </span>
  );
  return block ? <div className="connector-type-badge-block">{badge}</div> : badge;
}
