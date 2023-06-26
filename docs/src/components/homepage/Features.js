/* eslint-disable no-undef */
import React from "react";
import clsx from "clsx";
import styles from "./features.module.scss";
import Link from "@docusaurus/Link";

const FeatureList = [
  {
    title: "Tutorial",
    Svg: require("@site/static/img/homepage/tutorial.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "Go to Tutorial",
      url: "#",
      target: "_blank",
    },
  },
  {
    title: "Product Docs",
    Svg: require("@site/static/img/homepage/book-open.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "Go to Docs",
      url: "#",
      target: "_blank",
    },
  },
  {
    title: "Meltano Hub",
    Svg: require("@site/static/img/homepage/hub.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "Go to Hub",
      url: "#",
      target: "_blank",
    },
  },
  {
    title: "Meltano Cloud",
    Svg: require("@site/static/img/homepage/cloud.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "Go to Cloud",
      url: "#",
      target: "_blank",
    },
  },
  {
    title: "SDK in Action",
    Svg: require("@site/static/img/homepage/rocket.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "View Examples",
      url: "#",
      target: "_blank",
    },
  },
  {
    title: "SDK",
    Svg: require("@site/static/img/homepage/sdk.svg").default,
    description: (
      <>
        Get started with Meltano and run an EL[T] pipeline with a data source
        and destination of your choosing.
      </>
    ),
    link: {
      title: "Go to SDK",
      url: "#",
      target: "_blank",
    },
  },
];

function Feature({ Svg, title, description, link }) {
  return (
    <div className={styles.card}>
      <div className="text-left z-10">
        <div className={styles.header}>
          <Svg className={styles.featureSvg} role="img" />
          <h5 className="text-3xl font-semibold ms-1">{title}</h5>
        </div>
        <p className="p1 mb-3">{description}</p>
        <Link to={link.url} target={link.target} className="btn main-btn">
          {link.title}
        </Link>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className="my-20">
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
