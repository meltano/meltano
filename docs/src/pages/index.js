import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageEngineers from '../components/homepage/Engineers';
import SaaS from '@site/static/img/engineers/1-saas-api.svg'
import Database from '@site/static/img/engineers/2-database.svg'
import File from '@site/static/img/engineers/3-file.svg'
import TargetDatabase from '@site/static/img/engineers/5-database.svg'
import TargetVectorDB from '@site/static/img/engineers/6-vector-db.svg'
import TargetWarehouse from '@site/static/img/engineers/7-data-warehouse.svg'
import TargetLake from '@site/static/img/engineers/8-data-lake.svg'
import HomepageFeatures from '../components/homepage/Features';

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
  const engineers = {
    engineersTitle: 'Meltano gives data engineers <br><em>control and visibility</em><br> of their pipelines',
    engineersText: 'No more black box. Let your creativity flow.',
    engineersHead: { engineersHeadLeft: 'Sources', engineersHeadRight: 'Destinations' },
    engineersTable: [
      { engineersTableText: 'SaaS API', engineersTableImage: SaaS },
      { engineersTableText: 'Database', engineersTableImage: Database },
      { engineersTableText: 'File', engineersTableImage: File },
      {
        engineersTableText: 'Custom Source',
        engineersTableImage: SaaS
      },
      { engineersTableText: 'Database', engineersTableImage: TargetDatabase },
      { engineersTableText: 'Vector DB', engineersTableImage: TargetVectorDB },
      {
        engineersTableText: 'Data Warehouse',
        engineersTableImage: TargetWarehouse
      },
      { engineersTableText: 'Data Lake', engineersTableImage: TargetLake }
    ]
  }
  return (
    <Layout
      title={siteConfig.title}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      <main className="mb-10">
        <HomepageFeatures />
        <HomepageEngineers data={engineers} />
        <HomepageFindOutMore />
      </main>
    </Layout>
  );
}
