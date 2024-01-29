/* eslint-disable no-undef */
import React from 'react';
import styles from './features.module.scss';
import Link from '@docusaurus/Link';

const FeatureList = [
  {
    title: 'Tutorial',
    Svg: require('@site/static/img/homepage/tutorial.svg').default,
    description: (
      <>
        Get started with Meltano and run data pipelines with a source
        and destination of your choosing.
      </>
    ),
    link: {
      title: 'View Tutorials',
      url: 'tutorials/',
    },
  },
  {
    title: 'Product Docs',
    Svg: require('@site/static/img/homepage/book-open.svg').default,
    description: (
      <>
        Dive into how Meltano works and how to use it to build your data-powered applications.
      </>
    ),
    link: {
      title: 'Go to Docs',
      url: '/guide',
    },
  },
  {
    title: 'Meltano Hub',
    Svg: require('@site/static/img/homepage/hub.svg').default,
    description: (
      <>
        Explore the library of 600+ connectors and tools within the Meltano ecosystem.
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
        Build your own Meltano connector to move data from any source to any destination.
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
        Explore many of the connectors built with the Meltano SDK in their home on GitHub: Meltano Labs.
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
      <div className="text-left z-10">
        <div className={styles.header}>
          <Svg className={styles.featureSvg} role="img" />
          <h4 className="text-2xl font-semibold ms-2">{title}</h4>
        </div>
        <p className="p2 mt-3 mb-6">{description}</p>
        {/* eslint-disable-next-line react/prop-types */}
        <Link to={link.url} target={link.target} className="btn main-btn">
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
