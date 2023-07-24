import React from 'react';
// eslint-disable-next-line no-unused-vars
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '../components/homepage/Features';
// eslint-disable-next-line no-unused-vars
import HomepageUseCases from '../components/homepage/UseCases';

import styles from './index.module.scss';
import HomepageFindOutMore from '../components/homepage/FindOutMore';

function HomepageHeader() {
  // const { siteConfig } = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className="container md:mt-20">
        <h1 className="text-4xl md:text-6xl font-bold my-10">
          Explore <span className="brackets">using</span> Meltano
        </h1>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      <main className="mb-10">
        <HomepageFeatures />
        {/* <HomepageUseCases /> */}
        <HomepageFindOutMore />
      </main>
    </Layout>
  );
}
