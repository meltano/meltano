import React from 'react';
import LinkItem from '@theme/Footer/LinkItem';
// eslint-disable-next-line react/prop-types
function ColumnLinkItem({ item }) {
  // eslint-disable-next-line react/prop-types
  return item.html ? (
    <li
      className="footer__item"
      // Developer provided the HTML, so assume it's safe.
      // eslint-disable-next-line react/no-danger, react/prop-types
      dangerouslySetInnerHTML={{ __html: item.html }}
    />
  ) : (
    // eslint-disable-next-line react/prop-types
    <li key={item.href ?? item.to} className="footer__item">
      <LinkItem item={item} />
    </li>
  );
}
// eslint-disable-next-line react/prop-types
function Column({ column }) {
  return (
    <div className="col footer__col p-0">
      {/* eslint-disable-next-line react/prop-types */}
      <div className="footer__title">{column.title}</div>
      <ul className="footer__items clean-list">
        {/* eslint-disable-next-line react/prop-types */}
        {column.items.map((item, i) => (
          <ColumnLinkItem key={i} item={item} />
        ))}
      </ul>
    </div>
  );
}
// eslint-disable-next-line react/prop-types
export default function FooterLinksMultiColumn({ columns }) {
  return (
    <div className="row footer__links grid grid-cols-2 md:grid-cols-4 m-0">
      {/* eslint-disable-next-line react/prop-types */}
      {columns.map((column, i) => (
        <Column key={i} column={column} />
      ))}
    </div>
  );
}
