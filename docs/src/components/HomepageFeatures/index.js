import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Getting Started',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        <ul>
          <li><a href="#">Part 1</a></li>
          <li><a href="#">Part 2</a></li>
          <li><a href="#">Part 3</a></li>
          <li><a href="#">Part 4</a></li>
          <li><a href="#">Meltano at a Glance</a></li>
        </ul>
      </>
    ),
  },
  {
    title: 'Install & Deploy',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        <ul>
          <li><a href="#">Installation Guide</a></li>
          <li><a href="#">Deploy using GitHub Actions</a></li>
          <li><a href="#">Deploy using Kubernetes</a></li>
          <li><a href="#">Meltano Cloud</a></li>
        </ul>
      </>
    ),
  },
  {
    title: 'CLI Reference',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        <ul>
          <li><a href="#">CLI Reference</a></li>
          <li><a href="#">Add a Loader</a></li>
          <li><a href="#">Add an Extractor</a></li>
        </ul>
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
