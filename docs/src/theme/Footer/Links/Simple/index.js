import React from 'react';
import LinkItem from '@theme/Footer/LinkItem';
function Separator() {
  return <span className="footer__link-separator">·</span>;
}
// eslint-disable-next-line react/prop-types
function SimpleLinkItem({item}) {
  // eslint-disable-next-line react/prop-types
  return item.html ? (
    <span
      className="footer__link-item"
      // Developer provided the HTML, so assume it's safe.
      // eslint-disable-next-line react/no-danger, react/prop-types
      dangerouslySetInnerHTML={{__html: item.html}}
    />
  ) : (
    <LinkItem item={item} />
  );
}
// eslint-disable-next-line react/prop-types
export default function FooterLinksSimple({links}) {
  return (
    <div className="footer__links text--center">
      <div className="footer__links">
        {/* eslint-disable-next-line react/prop-types */}
        {links.map((item, i) => (
          <React.Fragment key={i}>
            <SimpleLinkItem item={item} />
            {/* eslint-disable-next-line react/prop-types */}
            {links.length !== i + 1 && <Separator />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
