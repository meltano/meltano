import React from 'react';
import { useThemeConfig } from '@docusaurus/theme-common';
import { useNavbarMobileSidebar } from '@docusaurus/theme-common/internal';
import NavbarItem from '@theme/NavbarItem';
import NavbarLogo from '@theme/Navbar/Logo';
import SearchBar from '@theme/SearchBar';
import NavbarSearch from '@theme/Navbar/Search';
import GithubLogo from '@site/static/img/footer/github.svg';
import SlackLogo from '@site/static/img/footer/slack.svg';
import TwitterLogo from '@site/static/img/footer/twitter.svg';
import LinkedinLogo from '@site/static/img/footer/linkedin.svg';
// eslint-disable-next-line no-unused-vars
import FacebookLogo from '@site/static/img/footer/facebook.svg';
// eslint-disable-next-line no-unused-vars
import InstagramLogo from '@site/static/img/footer/instagram.svg';
import YoutubeLogo from '@site/static/img/footer/youtube.svg';
import CrunchbaseLogo from '@site/static/img/footer/crunchbase.svg';
import styles from './primarymenu.module.scss';

function useNavbarItems() {
  // TODO temporary casting until ThemeConfig type is improved
  return useThemeConfig().navbar.items;
}
// The primary menu displays the navbar items
export default function NavbarMobilePrimaryMenu() {
  const mobileSidebar = useNavbarMobileSidebar();
  // TODO how can the order be defined for mobile?
  // Should we allow providing a different list of items?
  const items = useNavbarItems();
  return (
    <div className="primaryWrapper h-full container flex flex-col justify-between">
      <div className="mainNav my-10">
        <NavbarSearch className={'my-10 ' + styles.sidebarSearch}>
          <SearchBar />
        </NavbarSearch>
        <ul className="menu__list">
          {items.map((item, i) => (
            <NavbarItem
              mobile
              {...item}
              onClick={() => mobileSidebar.toggle()}
              key={i}
            />
          ))}
        </ul>
      </div>
      <div className="secondaryNav">
        <div className="navbar-sidebar__brand w-full flex justify-center mb-10">
          <NavbarLogo />
        </div>
        <div className="footer-soc-wrapper flex justify-between gap-3 order-1 sm:order-2 mb-10">
          <a href="https://github.com/meltano/meltano" className="opacity-50">
            <GithubLogo title="Github Logo" className={styles.menuSocIcon} />
          </a>
          <a href="https://meltano.com/slack" className="opacity-50">
            <SlackLogo title="Slack Logo" className={styles.menuSocIcon} />
          </a>
          <a href="https://twitter.com/meltanodata" className="opacity-50">
            <TwitterLogo title="Twitter Logo" className={styles.menuSocIcon} />
          </a>
          <a
            href="https://www.linkedin.com/company/meltano/"
            className="opacity-50"
          >
            <LinkedinLogo
              title="Linkedin Logo"
              className={styles.menuSocIcon}
            />
          </a>
          {/* <a href="#" className="opacity-50">
            <FacebookLogo
              title="Facebook Logo"
              className={styles.menuSocIcon}
            />
          </a> */}
          {/* <a href="#" className="opacity-50">
            <InstagramLogo
              title="Instagram Logo"
              className={styles.menuSocIcon}
            />
          </a> */}
          <a href="https://www.youtube.com/meltano" className="opacity-50">
            <YoutubeLogo title="Youtube Logo" className={styles.menuSocIcon} />
          </a>
          <a
            href="https://www.crunchbase.com/organization/meltano"
            className="opacity-50"
          >
            <CrunchbaseLogo
              title="Crunchbase Logo"
              className={styles.menuSocIcon}
            />
          </a>
        </div>
      </div>
    </div>
  );
}
