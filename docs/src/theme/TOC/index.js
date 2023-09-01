import React from 'react';
import clsx from 'clsx';
import TOCItems from '@theme/TOCItems';
import { useDoc } from '@docusaurus/theme-common/internal';
import styles from './styles.module.css';
import EditThisPage from '../EditThisPage';
// Using a custom className
// This prevents TOCInline/TOCCollapsible getting highlighted by mistake
const LINK_CLASS_NAME = 'table-of-contents__link toc-highlight';
const LINK_ACTIVE_CLASS_NAME = 'table-of-contents__link--active';
// eslint-disable-next-line react/prop-types
export default function TOC({ className, ...props }) {
  // eslint-disable-next-line react/prop-types
  const docs = props.type === 'docs';
  let metadata;
  let editUrl;

  if (docs) {
    metadata = useDoc().metadata;
    editUrl = metadata.editUrl;
  }

  return (
    <div
      className={clsx(
        styles.tableOfContents,
        'thin-scrollbar pb-16',
        className
      )}
    >
      <TOCItems
        {...props}
        linkClassName={LINK_CLASS_NAME}
        linkActiveClassName={LINK_ACTIVE_CLASS_NAME}
      />
      {docs && <EditThisPage editUrl={editUrl} />}
    </div>
  );
}
