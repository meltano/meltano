import React from 'react';
import clsx from 'clsx';
import { useLocation } from '@docusaurus/router';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import BlogSidebar from '@theme/BlogSidebar';
import Melty from '@site/static/img/melty.png';
import styles from './index.module.scss';

const CHANGELOG_TABS = [
  { label: 'Meltano Cloud', to: '/changelog/cloud' },
  { label: 'Meltano Open', to: '/changelog' },
];

function ChangelogSwitcher() {
  const { pathname } = useLocation();
  const isCloud = pathname.startsWith('/changelog/cloud');
  return (
    <div className={styles.changelogTabs}>
      {CHANGELOG_TABS.map((tab) => {
        const active = tab.to === '/changelog/cloud' ? isCloud : !isCloud;
        return (
          <Link
            key={tab.to}
            to={tab.to}
            className={clsx('changelog-tab', styles.changelogTab, {
              [styles.changelogTabActive]: active,
            })}
            aria-current={active ? 'page' : undefined}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}

function BackToChangelogsLink() {
  const { pathname } = useLocation();
  const backTo = pathname.startsWith('/changelog/cloud') ? '/changelog/cloud' : '/changelog';
  return (
    <Link to={backTo} className={clsx('changelog-back-link', styles.backLink)}>
      &larr; Back to Changelog
    </Link>
  );
}

export default function BlogLayout(props) {
  // eslint-disable-next-line react/prop-types
  const { sidebar, toc, children, isPostPage, ...layoutProps } = props;
  // eslint-disable-next-line react/prop-types
  const hasSidebar = sidebar && sidebar.items.length > 0;
  return (
    <Layout {...layoutProps}>
      {isPostPage ? (
        <div className={clsx(styles.backLinkWrapper, 'container')}>
          <BackToChangelogsLink />
        </div>
      ) : (
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
          <h1 className="text-4xl md:text-6xl font-bold mb-6 lg:mt-10">
            Changelog
          </h1>
          <ChangelogSwitcher />
        </div>
      )}
      <div className={clsx(styles.changelog, 'container')}>
        <div className="row">
          <BlogSidebar sidebar={sidebar} />
          <main
            className={clsx('col py-10 changelog-content', styles.changelogMain, {
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
