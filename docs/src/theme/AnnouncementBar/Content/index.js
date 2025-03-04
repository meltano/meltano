import React from 'react';
import clsx from 'clsx';
import { useThemeConfig } from '@docusaurus/theme-common';
import styles from './styles.module.css';
export default function AnnouncementBarContent(props) {
  const { announcementBar } = useThemeConfig();
  const { content } = announcementBar;
  return (
    <div
      {...props}
      // eslint-disable-next-line react/prop-types
      className={clsx(styles.content, props.className)}
      // Developer provided the HTML, so assume it's safe.
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
}
