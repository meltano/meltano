import React from 'react';
import { useThemeConfig, ErrorCauseBoundary } from '@docusaurus/theme-common';
import {
  splitNavbarItems,
  useNavbarMobileSidebar,
} from '@docusaurus/theme-common/internal';
import clsx from 'clsx';
import NavbarItem from '@theme/NavbarItem';
import NavbarColorModeToggle from '@theme/Navbar/ColorModeToggle';
import SearchBar from '@theme/SearchBar';
import NavbarMobileSidebarToggle from '@theme/Navbar/MobileSidebar/Toggle';
import NavbarLogo from '@theme/Navbar/Logo';
import NavbarSearch from '@theme/Navbar/Search';
import styles from './styles.module.css';
function useNavbarItems() {
  // TODO temporary casting until ThemeConfig type is improved
  return useThemeConfig().navbar.items;
}
// eslint-disable-next-line react/prop-types
function NavbarItems({ items }) {
  return (
    <>
      {/* eslint-disable-next-line react/prop-types */}
      {items.map((item, i) => (
        <ErrorCauseBoundary
          key={i}
          onError={(error) =>
            new Error(
              `A theme navbar item failed to render.
Please double-check the following navbar item (themeConfig.navbar.items) of your Docusaurus config:
${JSON.stringify(item, null, 2)}`,
              { cause: error }
            )
          }
        >
          <NavbarItem {...item} />
        </ErrorCauseBoundary>
      ))}
    </>
  );
}
// eslint-disable-next-line react/prop-types
function NavbarContentLayout({ left, right }) {
  return (
    <div className="navbar__inner relative">
      <NavbarLogo />
      <div
        className={clsx('navbar__items navbar__items--left', styles.navbarLeft)}
      >
        {left}
      </div>
      <div
        className={clsx(
          'navbar__items navbar__items--right',
          styles.navbarRight
        )}
      >
        {right}
      </div>
    </div>
  );
}
export default function NavbarContent() {
  const mobileSidebar = useNavbarMobileSidebar();
  const items = useNavbarItems();
  const [leftItems, rightItems] = splitNavbarItems(items);
  const searchBarItem = items.find((item) => item.type === 'search');
  return (
    <NavbarContentLayout
      left={<NavbarItems items={leftItems} />}
      right={
        <>
          <NavbarItems items={rightItems} />
          <NavbarColorModeToggle />
          {!searchBarItem && (
            <NavbarSearch>
              <SearchBar />
            </NavbarSearch>
          )}
          {!mobileSidebar.disabled && <NavbarMobileSidebarToggle />}
        </>
      }
    />
  );
}
