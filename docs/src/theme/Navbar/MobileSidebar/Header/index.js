import React from 'react';
import { useNavbarMobileSidebar } from '@docusaurus/theme-common/internal';
import { translate } from '@docusaurus/Translate';
import IconClose from '@theme/Icon/Close';
import clsx from 'clsx';
import styles from './styles.module.css';

function CloseButton() {
  const mobileSidebar = useNavbarMobileSidebar();
  return (
    <button
      type="button"
      aria-label={translate({
        id: 'theme.docs.sidebar.closeSidebarButtonAriaLabel',
        message: 'Close navigation bar',
        description: 'The ARIA label for close button of mobile sidebar',
      })}
      className="clean-btn navbar-sidebar__close mt-12 mr-0"
      onClick={() => mobileSidebar.toggle()}
    >
      <IconClose color="var(--ifm-color-emphasis-600)" />
    </button>
  );
}
export default function NavbarMobileSidebarHeader() {
  return (
    <div
      className={clsx(
        'navbar-sidebar__brand absolute',
        styles.closeButtonWrapper
      )}
    >
      <CloseButton />
    </div>
  );
}
