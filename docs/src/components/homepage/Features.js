import React from 'react';
import styles from './features.module.scss';
import Link from '@docusaurus/Link';

const FeatureList = [
  {
    title: 'Open',
    Svg: require('@site/static/img/homepage/open.svg').default,
    description: (
      <>
        Open source (MIT). The core Singer-based ELT engine. Bring your own
        orchestration, storage, and infrastructure. Fully self-managed.
      </>
    ),
    link: {
      title: 'Get Started',
      url: '/getting-started/meltano-at-a-glance',
    },
  },
  {
    title: 'Cloud',
    Svg: require('@site/static/img/homepage/cloud.svg').default,
    description: (
      <>
        Fully managed hosted service. Hosted pipelines, workspaces, secrets, and
        monitoring. No infrastructure to run. Connect with us, get access and
        start moving data in minutes.{' '}
      </>
    ),
    link: {
      title: 'Get Started',
      url: '/getting-started/cloud-overview',
    },
  },
  {
    title: 'Reference',
    Svg: require('@site/static/img/homepage/book-open.svg').default,
    description: (
      <>
        Browse the full Meltano reference documentation — CLI commands, settings,
        plugin definition syntax, and more.
      </>
    ),
    link: {
      title: 'View Reference',
      url: '/reference',
    },
  },
  {
    title: 'Meltano Hub',
    Svg: require('@site/static/img/homepage/hub.svg').default,
    description: (
      <>
        Explore the library of 600+ connectors and tools within the Meltano
        ecosystem.
      </>
    ),
    link: {
      title: 'Go to Hub',
      url: 'https://hub.meltano.com',
      target: '_blank',
    },
  },
  {
    title: 'SDK',
    Svg: require('@site/static/img/homepage/sdk.svg').default,
    description: (
      <>
        Build your own Meltano connector to move data from any source to any
        destination.
      </>
    ),
    link: {
      title: 'Go to SDK',
      url: 'https://sdk.meltano.com',
      target: '_blank',
    },
  },
  {
    title: 'SDK in Action',
    Svg: require('@site/static/img/homepage/rocket.svg').default,
    description: (
      <>
        Explore many of the connectors built with the Meltano SDK in their home
        on GitHub: Meltano Labs.
      </>
    ),
    link: {
      title: 'View Examples',
      url: 'https://github.com/meltanolabs/',
      target: '_blank',
    },
  },
];

// eslint-disable-next-line react/prop-types
function Feature({ Svg, title, description, link }) {
  return (
    <div className={styles.card}>
      <div className="text-left z-10 flex flex-col h-full">
        <div className={styles.header}>
          <Svg className={styles.featureSvg} role="img" />
          <h4 className="text-2xl font-semibold ms-2">{title}</h4>
        </div>
        <p className="p2 mt-3 mb-6 flex-1">{description}</p>
        {/* eslint-disable-next-line react/prop-types */}
        <Link to={link.url} target={link.target} className="btn main-btn mt-auto">
          {/* eslint-disable-next-line react/prop-types */}
          {link.title}
        </Link>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className="md:my-20">
      <div className="container relative">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
