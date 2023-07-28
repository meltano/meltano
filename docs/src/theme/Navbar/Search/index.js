import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
// eslint-disable-next-line react/prop-types
export default function NavbarSearch({children, className}) {
  return <div className={clsx(className, styles.searchBox)}>{children}</div>;
}
