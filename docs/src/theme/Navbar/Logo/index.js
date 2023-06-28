import React from "react";
import Link from "@docusaurus/Link";
import styles from "./styles.module.css";

export default function NavbarLogo() {
  return (
    <div class="navbar__brand">
      <a href="https://meltano.com/">
        <div class="navbar__logo" />
      </a>
      <Link class="navbar__brand" href="/">
        <b class={"navbar__title text--truncate " + styles.docsLink}>Docs</b>
      </Link>
    </div>
  );
}
