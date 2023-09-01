/* eslint-disable no-undef */
import React from 'react';
import styles from './findoutmore.module.scss';
import Link from '@docusaurus/Link';

const FindOutMoreList = [
  {
    title: <>Visit Our Blog</>,
    Svg: require('@site/static/img/homepage/melty.svg').default,
    link: {
      url: 'https://meltano.com/blog/',
      target: '_blank',
    },
  },
  {
    title: <>Join Our Slack Community</>,
    Svg: require('@site/static/img/homepage/slack.svg').default,
    link: {
      url: 'https://meltano.com/slack/',
      target: '_blank',
    },
  },
  {
    title: <>Subscribe to our Newsletter</>,
    Svg: require('@site/static/img/homepage/subscribe.svg').default,
    link: {
      url: 'https://meltano.com/lp/meltastic-newsletter/',
      target: '_blank',
    },
  },
];

// eslint-disable-next-line react/prop-types
function IconLink({ Svg, title, link }) {
  if (title)
    return (
      <Link
        // eslint-disable-next-line react/prop-types
        to={link.url}
        // eslint-disable-next-line react/prop-types
        target={link.target}
        className="flex flex-col text-center items-center basis-1/3 lg:basis-1/6"
      >
        <Svg className={'mb-6 p-2 ' + styles.findOutMoreSvg} role="img" />
        <p className={'p1 ' + styles.findOutMoreTitle}>{title}</p>
      </Link>
    );
  return <div></div>;
}

export default function HomepageFindOutMore() {
  return (
    <section className="my-10 md:my-20">
      <div className="container relative">
        <h2 className="text-center font-bold pb-10 md:pb-20">Find Out More!</h2>
        <div className="flex gap-2 justify-center">
          {FindOutMoreList.map((props, idx) => (
            <IconLink key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
