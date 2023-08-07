import React from 'react';
import clsx from 'clsx';
import { ThemeClassNames } from '@docusaurus/theme-common';
import { useDocsSidebar } from '@docusaurus/theme-common/internal';
import { useLocation } from '@docusaurus/router';
import DocSidebar from '@theme/DocSidebar';
import styles from './styles.module.css';
// Reset sidebar state when sidebar changes
// Use React key to unmount/remount the children
// See https://github.com/facebook/docusaurus/issues/3414
// eslint-disable-next-line react/prop-types
function ResetOnSidebarChange({ children }) {
  const sidebar = useDocsSidebar();
  return (
    <React.Fragment key={sidebar?.name ?? 'noSidebar'}>
      {children}
    </React.Fragment>
  );
}
export default function DocPageLayoutSidebar({
  // eslint-disable-next-line react/prop-types
  sidebar,
  // eslint-disable-next-line react/prop-types
  hiddenSidebarContainer,
  // eslint-disable-next-line react/prop-types
  hiddenSidebar,
}) {
  const { pathname } = useLocation();

  return (
    <aside
      className={clsx(
        ThemeClassNames.docs.docSidebarContainer,
        styles.docSidebarContainer,
        hiddenSidebarContainer && styles.docSidebarContainerHidden
      )}
      onTransitionEnd={(e) => {
        if (!e.currentTarget.classList.contains(styles.docSidebarContainer)) {
          return;
        }
      }}
    >
      <ResetOnSidebarChange>
        <div
          className={clsx(
            styles.sidebarViewport,
            hiddenSidebar && styles.sidebarViewportHidden
          )}
        >
          <DocSidebar
            sidebar={sidebar}
            path={pathname}
            isHidden={hiddenSidebar}
          />
        </div>
      </ResetOnSidebarChange>
    </aside>
  );
}
