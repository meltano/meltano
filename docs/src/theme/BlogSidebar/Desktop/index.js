import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import { translate } from "@docusaurus/Translate";
import styles from "./styles.module.css";
export default function BlogSidebarDesktop({ sidebar }) {
  return (
    <aside className={clsx(styles.sidebarWrapper, "col col--2")}>
      <nav
        className={clsx(styles.sidebar, "thin-scrollbar py-10")}
        aria-label={translate({
          id: "theme.blog.sidebar.navAriaLabel",
          message: "Blog recent posts navigation",
          description: "The ARIA label for recent posts in the blog sidebar",
        })}
      >
        <div className={clsx(styles.sidebarItemTitle, "margin-bottom--md")}>
          {sidebar.title}
        </div>
        <ul className={clsx(styles.sidebarItemList, "clean-list")}>
          {sidebar.items.map((item) => (
            <li
              key={item.permalink}
              className={clsx(styles.sidebarItem, "my-4")}
            >
              <Link
                isNavLink
                to={item.permalink}
                className={styles.sidebarItemLink}
                activeClassName={styles.sidebarItemLinkActive}
              >
                {item.title}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
