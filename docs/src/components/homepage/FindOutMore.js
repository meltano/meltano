/* eslint-disable no-undef */
import React from "react";
import clsx from "clsx";
import styles from "./features.module.scss";
import Link from "@docusaurus/Link";

const FindOutMoreList = [
  {},
  {
    title: (
      <>
        Visit Our
        <br />
        Blog
      </>
    ),
    Svg: require("@site/static/img/homepage/melty.svg").default,
    link: {
      url: "#",
      target: "_blank",
    },
  },
  {
    title: (
      <>
        Join Our Slack
        <br />
        Community
      </>
    ),
    Svg: require("@site/static/img/homepage/slack.svg").default,
    link: {
      url: "#",
      target: "_blank",
    },
  },
  {
    title: (
      <>
        Subscribe to our
        <br />
        Newsletter
      </>
    ),
    Svg: require("@site/static/img/homepage/subscribe.svg").default,
    link: {
      url: "#",
      target: "_blank",
    },
  },
];

function IconLink({ Svg, title, link }) {
  if (title)
    return (
      <Link
        to={link.url}
        target={link.target}
        className="flex flex-col text-center items-center"
      >
        <Svg className={"mb-6 " + styles.featureSvg} role="img" />
        <p className="p1 font-semibold">{title}</p>
      </Link>
    );
  return <div></div>;
}

export default function HomepageFindOutMore() {
  return (
    <section className="my-20">
      <div className="container relative">
        <h2
          className={
            "text-center text-5xl font-bold pb-20 " + styles.usecaseHeader
          }
        >
          Find Out More!
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5">
          {FindOutMoreList.map((props, idx) => (
            <IconLink key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
