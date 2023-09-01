import React from 'react';
import clsx from 'clsx';
import { useDocsSidebar } from '@docusaurus/theme-common/internal';
import DocBreadcrumbs from '@theme/DocBreadcrumbs';
import styles from './styles.module.css';
export default function DocPageLayoutMain({
  // eslint-disable-next-line react/prop-types
  hiddenSidebarContainer,
  // eslint-disable-next-line react/prop-types
  children,
}) {
  const sidebar = useDocsSidebar();
  return (
    <main
      className={clsx(
        styles.docMainContainer,
        (hiddenSidebarContainer || !sidebar) && styles.docMainContainerEnhanced
      )}
    >
      <DocBreadcrumbs />
      <div
        className={clsx(
          'padding-bottom--lg',
          styles.docItemWrapper,
          hiddenSidebarContainer && styles.docItemWrapperEnhanced
        )}
      >
        {children}
      </div>
    </main>
  );
}
