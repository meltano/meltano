import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

export default function NavbarLogo() {
  return (
    <div className="navbar__brand">
      <Link className="navbar__brand" href="/">
        <div className="navbar__logo" />
        <b className={'navbar__title text--truncate ' + styles.docsLink}>
          Docs
        </b>
      </Link>
    </div>
  );
}
