import React from 'react';
import PropTypes from 'prop-types';
import styles from './features.module.scss';
import Link from '@docusaurus/Link';

const openEdition = {
  Svg: require('@site/static/img/homepage/open.svg').default,
  name: 'Open',
  desc: 'The open-source, self-hosted foundation of Meltano. Own every part of your data infrastructure, on your own servers, free forever. Best for teams with DevOps capacity who want full control with zero vendor dependency.',
  features: [
    { text: 'You host and manage everything on your own servers', type: 'base' },
    { text: 'Access to 600+ built-in connectors', type: 'base' },
    { text: 'Free, you pay only for your own infra', type: 'base' },
  ],
  cta: { title: 'Get Started', url: '/meltano-open/meltano-at-a-glance' },
};

const cloudEdition = {
  Svg: require('@site/static/img/homepage/cloud.svg').default,
  name: 'Cloud',
  desc: 'A fully managed hosted service built on top of Meltano Open. Pipelines, workspaces, secrets, and monitoring are all handled for you. No infrastructure to provision, patch, or maintain. Best for data teams who want to move fast without managing the plumbing.',
  features: [
    { text: 'Meltano hosts, scales, and maintains everything for you', type: 'base' },
    { text: 'Access to 600+ built-in and custom connectors', type: 'base' },
    { text: 'Paid plans based on compute hours', type: 'base' },
    { text: 'Built-in pipeline monitoring and alerts', type: 'base' },
  ],
  cta: { title: 'Get Started', url: '/meltano-cloud/cloud-overview' },
};

const FeatureList = [
  {
    title: 'Reference',
    Svg: require('@site/static/img/homepage/book-open.svg').default,
    description: (
      <>
        Browse the full Meltano reference documentation — CLI commands, settings,
        plugin definition syntax, and more.
      </>
    ),
    link: { title: 'View Reference', url: '/reference' },
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
    link: { title: 'Go to Hub', url: 'https://hub.meltano.com', target: '_blank' },
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
    link: { title: 'Go to SDK', url: 'https://sdk.meltano.com', target: '_blank' },
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
    link: { title: 'View Examples', url: 'https://github.com/meltanolabs/', target: '_blank' },
  },
];

// Each direct child maps to one subgrid row: header / desc / metric / features / cta
function EditionCard({ Svg, name, desc, metric, metricLabel, chip, features, cta }) {
  return (
    <div className="edition-card">
      <div className={styles.header}>
        <Svg className={styles.featureSvg} role="img" />
        <h4 className="text-2xl font-semibold ms-2">{name}</h4>
      </div>

      <p className="p2">{desc}</p>

      <ul className="edition-features">
        {features.map((f, i) => (
          <li key={i} className="edition-features__item">
            {f.type === 'add'
              ? <span className="edition-features__add">+</span>
              : <span className="edition-features__check">✓</span>
            }
            {f.text}
          </li>
        ))}
      </ul>

      <Link to={cta.url} className="btn main-btn">
        {cta.title}
      </Link>
    </div>
  );
}

EditionCard.propTypes = {
  Svg: PropTypes.elementType.isRequired,
  name: PropTypes.string.isRequired,
  desc: PropTypes.string.isRequired,
  metric: PropTypes.string,
  metricLabel: PropTypes.string,
  chip: PropTypes.string,
  features: PropTypes.arrayOf(PropTypes.shape({
    text: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
  })).isRequired,
  cta: PropTypes.shape({
    title: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  }).isRequired,
};

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
        <div className="edition-grid">
          <EditionCard {...openEdition} />
          <EditionCard {...cloudEdition} />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
