import React from "react";
import clsx from "clsx";
import MeltanoLogo from "@site/static/img/footer/meltano.svg";
import FloatingIsland from "@site/static/img/footer/floating.png";
import styles from "./layout.module.scss";

export default function FooterLayout({ style, links, logo, copyright }) {
  return (
    <footer
      className={clsx("footer", {
        "footer--dark": style === "dark",
      })}
    >
      <div className="container">
        <div
          className={
            "my-10 flex flex-col lg:flex-row justify-between " +
            styles.background
          }
        >
          <MeltanoLogo
            title="Meltano"
            className="footer-soc-icon grow-0 me-32 mb-8"
          />
          <div className="grow">{links}</div>
          <img
            src={FloatingIsland}
            alt="Floating Island"
            className="footer-soc-icon grow-0 ms-16 hidden xl:block"
          />
        </div>
        {(logo || copyright) && (
          <div className="footer__bottom text--center">
            {logo && <div className="margin-bottom--sm">{logo}</div>}
            {copyright}
          </div>
        )}
      </div>
    </footer>
  );
}
