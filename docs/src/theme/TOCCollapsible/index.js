import React from 'react';
import clsx from 'clsx';
import {useCollapsible, Collapsible} from '@docusaurus/theme-common';
import TOCItems from '@theme/TOCItems';
import CollapseButton from '@theme/TOCCollapsible/CollapseButton';
import styles from './styles.module.css';
export default function TOCCollapsible({
  // eslint-disable-next-line react/prop-types
  toc,
  // eslint-disable-next-line react/prop-types
  className,
  // eslint-disable-next-line react/prop-types
  minHeadingLevel,
  // eslint-disable-next-line react/prop-types
  maxHeadingLevel,
}) {
  const {collapsed, toggleCollapsed} = useCollapsible({
    initialState: true,
  });
  return (
    <div
      className={clsx(
        styles.tocCollapsible,
        !collapsed && styles.tocCollapsibleExpanded,
        className,
      )}>
      <CollapseButton collapsed={collapsed} onClick={toggleCollapsed} />
      <Collapsible
        lazy
        className={styles.tocCollapsibleContent}
        collapsed={collapsed}>
        <TOCItems
          toc={toc}
          minHeadingLevel={minHeadingLevel}
          maxHeadingLevel={maxHeadingLevel}
        />
      </Collapsible>
    </div>
  );
}
