import React from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import isInternalUrl from '@docusaurus/isInternalUrl';
// eslint-disable-next-line no-unused-vars
import IconExternalLink from '@theme/Icon/ExternalLink';
// eslint-disable-next-line react/prop-types
export default function FooterLinkItem({ item }) {
  // eslint-disable-next-line react/prop-types
  const { to, href, label, prependBaseUrlToHref, ...props } = item;
  const toUrl = useBaseUrl(to);
  const normalizedHref = useBaseUrl(href, { forcePrependBaseUrl: true });
  return (
    <Link
      className="footer__link-item"
      {...(href
        ? {
          href: prependBaseUrlToHref ? normalizedHref : href,
        }
        : {
          to: toUrl,
        })}
      {...props}
    >
      {label}
      {href && !isInternalUrl(href)}
    </Link>
  );
}
