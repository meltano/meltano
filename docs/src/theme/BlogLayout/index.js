import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import BlogSidebar from '@theme/BlogSidebar';
import Melty from '@site/static/img/melty.png';
import styles from './index.module.scss';

export default function BlogLayout(props) {
  // eslint-disable-next-line react/prop-types
  const { sidebar, toc, children, ...layoutProps } = props;
  // eslint-disable-next-line react/prop-types
  const hasSidebar = sidebar && sidebar.items.length > 0;
  return (
    <Layout {...layoutProps}>
      <div
        className={clsx(
          styles.changelogHeader,
          'relative w-full bg-black text-white flex flex-col items-center py-16 md:py-24'
        )}
      >
        <img
          src={Melty}
          alt="Melty"
          className={clsx(styles.melty, '-mb-16 hidden lg:block')}
        />
        <h1 className="text-4xl md:text-6xl font-bold mb-10 lg:mt-10">
          Changelog
        </h1>
        <a href="https://meltano.com/lp/meltastic-newsletter/" className="btn main-btn">
          Subscribe to Updates
        </a>
      </div>
      <div className={clsx(styles.changelog, 'container')}>
        <div className="row">
          <BlogSidebar sidebar={sidebar} />
          <main
            className={clsx('col py-10 changelog-content', {
              'col--8': hasSidebar,
              'col--10 col--offset-1': !hasSidebar,
            })}
            itemScope
            itemType="http://schema.org/Blog"
          >
            {children}
          </main>
          {toc && <div className={clsx(styles.toc, 'col col--2')}>{toc}</div>}
        </div>
      </div>
    </Layout>
  );
}
