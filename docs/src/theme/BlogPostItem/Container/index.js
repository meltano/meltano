import React from 'react';
import clsx from 'clsx';
import { useBaseUrlUtils } from '@docusaurus/useBaseUrl';
import { useBlogPost } from '@docusaurus/theme-common/internal';
import styles from './styles.module.css';

// eslint-disable-next-line react/prop-types
export default function BlogPostItemContainer({ children, className }) {
  const { frontMatter, assets, metadata } = useBlogPost();
  const { withBaseUrl } = useBaseUrlUtils();
  const image = assets.image ?? frontMatter.image;
  const regex = /\b\d{1,2},\s/;
  const date = metadata.formattedDate.replace(regex, '');
  const dateArray = date.split(' ');

  return (
    <div className="flex flex-col md:flex-row">
      <div
        className={clsx(
          'w-full md:w-24 h-16 flex flex-col px-2 py-3 margin-bottom--xl text-center shrink-0',
          styles.date
        )}
      >
        <span className={styles.month}>{dateArray[0]}</span>
        <span className={styles.year}>{dateArray[1]}</span>
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
