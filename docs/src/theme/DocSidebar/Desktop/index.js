import React from 'react';
import clsx from 'clsx';
import { useThemeConfig } from '@docusaurus/theme-common';
import Logo from '@theme/Logo';
import Content from '@theme/DocSidebar/Desktop/Content';
import styles from './styles.module.css';
// eslint-disable-next-line react/prop-types
function DocSidebarDesktop({ path, sidebar, isHidden }) {
  const {
    navbar: { hideOnScroll },
  } = useThemeConfig();
  return (
    <div
      className={clsx(
        styles.sidebar,
        'pb-24',
        hideOnScroll && styles.sidebarWithHideableNavbar,
        isHidden && styles.sidebarHidden
      )}
    >
      {hideOnScroll && <Logo tabIndex={-1} className={styles.sidebarLogo} />}
      <Content path={path} sidebar={sidebar} />
    </div>
  );
}
export default React.memo(DocSidebarDesktop);
