import React, { useState } from 'react';
import { useDocsSidebar } from '@docusaurus/theme-common/internal';
import Layout from '@theme/Layout';
import BackToTopButton from '@theme/BackToTopButton';
import DocPageLayoutSidebar from '@theme/DocPage/Layout/Sidebar';
import DocPageLayoutMain from '@theme/DocPage/Layout/Main';
import styles from './styles.module.css';
import SidebarArrow from '../../../components/SidebarArrow';
import clsx from 'clsx';
// eslint-disable-next-line react/prop-types
export default function DocPageLayout({ children }) {
  const sidebar = useDocsSidebar();
  const [hiddenSidebarContainer, setHiddenSidebarContainer] = useState(false);
  return (
    <Layout wrapperClassName={styles.docsWrapper}>
      <BackToTopButton />
      <div className={clsx(styles.docPage, 'doc-page')}>
        {sidebar && (
          <DocPageLayoutSidebar
            sidebar={sidebar.items}
            hiddenSidebarContainer={hiddenSidebarContainer}
            setHiddenSidebarContainer={setHiddenSidebarContainer}
          />
        )}

        <SidebarArrow
          className={styles.collapseSidebarButtonIcon}
          hiddenSidebarContainer={hiddenSidebarContainer}
          setHiddenSidebarContainer={setHiddenSidebarContainer}
          position="left"
        />
        <DocPageLayoutMain
          setHiddenSidebarContainer={setHiddenSidebarContainer}
        >
          {children}
        </DocPageLayoutMain>
      </div>
    </Layout>
  );
}
