import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import {useBaseUrlUtils} from '@docusaurus/useBaseUrl';
import ThemedImage from '@theme/ThemedImage';
import styles from './styles.module.css';
// eslint-disable-next-line react/prop-types
function LogoImage({logo}) {
  const {withBaseUrl} = useBaseUrlUtils();
  const sources = {
    // eslint-disable-next-line react/prop-types
    light: withBaseUrl(logo.src),
    // eslint-disable-next-line react/prop-types
    dark: withBaseUrl(logo.srcDark ?? logo.src),
  };
  return (
    <ThemedImage
      // eslint-disable-next-line react/prop-types
      className={clsx('footer__logo', logo.className)}
      // eslint-disable-next-line react/prop-types
      alt={logo.alt}
      sources={sources}
      // eslint-disable-next-line react/prop-types
      width={logo.width}
      // eslint-disable-next-line react/prop-types
      height={logo.height}
      // eslint-disable-next-line react/prop-types
      style={logo.style}
    />
  );
}
// eslint-disable-next-line react/prop-types
export default function FooterLogo({logo}) {
  // eslint-disable-next-line react/prop-types
  return logo.href ? (
    <Link
      // eslint-disable-next-line react/prop-types
      href={logo.href}
      className={styles.footerLogoLink}
      // eslint-disable-next-line react/prop-types
      target={logo.target}>
      <LogoImage logo={logo} />
    </Link>
  ) : (
    <LogoImage logo={logo} />
  );
}
