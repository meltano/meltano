import React from "react";
import Link from "@docusaurus/Link";
import styles from "./styles.module.css";

export default function NavbarLogo() {
  return (
    <div className="navbar__brand">
      <a href="https://meltano.com/">
        <div className="navbar__logo" />
      </a>
      <Link className="navbar__brand" href="/">
        <b className={"navbar__title text--truncate " + styles.docsLink}>
          Docs
        </b>
      </Link>
    </div>
  );
}
