import React from 'react';
import clsx from 'clsx';
import { useNavbarSecondaryMenu } from '@docusaurus/theme-common/internal';

export default function NavbarMobileSidebarLayout({
  // eslint-disable-next-line react/prop-types
  header,
  // eslint-disable-next-line react/prop-types
  primaryMenu,
  // eslint-disable-next-line react/prop-types
  secondaryMenu,
}) {
  const { shown: secondaryMenuShown } = useNavbarSecondaryMenu();
  return (
    <div className="navbar-sidebar overflow-hidden">
      {header}
      <div
        className={clsx('navbar-sidebar__items', {
          'navbar-sidebar__items--show-secondary': secondaryMenuShown,
        })}
      >
        <div className="navbar-sidebar__item menu">{primaryMenu}</div>
        <div className="navbar-sidebar__item menu">{secondaryMenu}</div>
      </div>
    </div>
  );
}
