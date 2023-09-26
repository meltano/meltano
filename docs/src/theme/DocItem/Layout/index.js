import React, { useState } from 'react';
import clsx from 'clsx';
import { useWindowSize } from '@docusaurus/theme-common';
import { useDoc } from '@docusaurus/theme-common/internal';
import DocItemPaginator from '@theme/DocItem/Paginator';
import DocVersionBanner from '@theme/DocVersionBanner';
// eslint-disable-next-line no-unused-vars
import DocItemFooter from '@theme/DocItem/Footer';
import DocItemTOCMobile from '@theme/DocItem/TOC/Mobile';
import DocItemTOCDesktop from '@theme/DocItem/TOC/Desktop';
import DocItemContent from '@theme/DocItem/Content';
import styles from './styles.module.css';
import SidebarArrow from '../../../components/SidebarArrow';
/**
 * Decide if the toc should be rendered, on mobile or desktop viewports
 */
function useDocTOC() {
  const { frontMatter, toc } = useDoc();
  const windowSize = useWindowSize();
  const hidden = frontMatter.hide_table_of_contents;
  const canRender = !hidden && toc.length > 0;
  const mobile = canRender ? <DocItemTOCMobile /> : undefined;
  const desktop =
    canRender && (windowSize === 'desktop' || windowSize === 'ssr') ? (
      <DocItemTOCDesktop />
    ) : undefined;
  return {
    hidden,
    mobile,
    desktop,
  };
}
// eslint-disable-next-line react/prop-types
export default function DocItemLayout({ children }) {
  const docTOC = useDocTOC();
  const [hiddenSidebarContainer, setHiddenSidebarContainer] = useState(false);
  return (
    <div className="container flex flex-col md:!px-8">
      <div className={clsx('flex', styles.docItem)}>
        <div
          className={clsx(
            'col !px-0 lg:!pr-4',
            !hiddenSidebarContainer && styles.docItemCol
          )}
        >
          <DocVersionBanner />
          {docTOC.mobile}
          <div className={clsx('padding-top--md', styles.docItemContainer)}>
            <article>
              <DocItemContent>{children}</DocItemContent>
              {/* <DocItemFooter /> */}
            </article>
            <DocItemPaginator />
          </div>
        </div>
        {docTOC.desktop && (
          <div
            className={clsx(
              'col col--3 flex justify-end',
              styles.tocContainer,
              hiddenSidebarContainer && styles.tocHiddenContainer
            )}
          >
            <SidebarArrow
              className={clsx(styles.collapseSidebarButtonIcon)}
              hiddenSidebarContainer={hiddenSidebarContainer}
              setHiddenSidebarContainer={setHiddenSidebarContainer}
              position="right"
            />
            <div
              className={clsx(
                styles.tocWrapper,
                hiddenSidebarContainer && styles.tocHidden
              )}
            >
              {docTOC.desktop}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
