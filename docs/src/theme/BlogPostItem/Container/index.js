import React from 'react';
import clsx from 'clsx';
import { useBaseUrlUtils } from '@docusaurus/useBaseUrl';
import { useDateTimeFormat } from '@docusaurus/theme-common/internal';
import { useBlogPost } from '@docusaurus/plugin-content-blog/client';
import styles from './styles.module.css';

// eslint-disable-next-line react/prop-types
export default function BlogPostItemContainer({ children, className }) {
  const { frontMatter, assets, metadata } = useBlogPost();
  const { withBaseUrl } = useBaseUrlUtils();
  const image = assets.image ?? frontMatter.image;
  const monthFormat = useDateTimeFormat({ month: 'long', timeZone: 'UTC' });
  const yearFormat = useDateTimeFormat({ year: 'numeric', timeZone: 'UTC' });
  const dateObj = new Date(metadata.date);
  const month = monthFormat.format(dateObj);
  const year = yearFormat.format(dateObj);

  return (
    <div className="flex flex-col md:flex-row">
      <div
        className={clsx(
          'w-full md:w-24 h-16 flex flex-col px-2 py-3 margin-bottom--xl text-center shrink-0',
          styles.date
        )}
      >
        <span className={styles.month}>{month}</span>
        <span className={styles.year}>{year}</span>
      </div>
      <article
        className={className}
        itemProp="blogPost"
        itemScope
        itemType="http://schema.org/BlogPosting"
      >
        {image && (
          <meta
            itemProp="image"
            content={withBaseUrl(image, { absolute: true })}
          />
        )}
        {children}
      </article>
    </div>
  );
}
