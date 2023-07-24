/* eslint-disable no-undef */
import React, { useState, useCallback } from 'react';
import { translate } from '@docusaurus/Translate';
import { prefersReducedMotion } from '@docusaurus/theme-common';
import clsx from 'clsx';
import styles from './sidebararrow.module.scss';

export default function SidebarArrow({
  // eslint-disable-next-line react/prop-types
  hiddenSidebarContainer,
  // eslint-disable-next-line react/prop-types
  setHiddenSidebarContainer,
  // eslint-disable-next-line react/prop-types
  position,
}) {
  const [hiddenSidebar, setHiddenSidebar] = useState(false);

  const toggleSidebar = useCallback(() => {
    if (hiddenSidebar) {
      setHiddenSidebar(false);
    }
    // onTransitionEnd won't fire when sidebar animation is disabled
    // fixes https://github.com/facebook/docusaurus/issues/8918
    if (!hiddenSidebar && prefersReducedMotion()) {
      setHiddenSidebar(true);
    }
    setHiddenSidebarContainer((value) => !value);
  }, [setHiddenSidebarContainer, hiddenSidebar]);

  return (
    <div className={styles.sidebarButtonWrapper}>
      <button
        type="button"
        title={translate({
          id: 'theme.docs.sidebar.collapseButtonTitle',
          message: 'Collapse sidebar',
          description: 'The title attribute for collapse button of doc sidebar',
        })}
        aria-label={translate({
          id: 'theme.docs.sidebar.collapseButtonAriaLabel',
          message: 'Collapse sidebar',
          description: 'The title attribute for collapse button of doc sidebar',
        })}
        className={clsx(
          hiddenSidebarContainer && styles.collapsed,
          styles.collapseSidebarButton
        )}
        onClick={toggleSidebar}
      >
        <svg
          width="32"
          height="32"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={clsx(
            styles.collapseSidebarButtonIcon,
            position === 'left'
              ? styles.collapseSidebarButtonIconLeft
              : styles.collapseSidebarButtonIconRight
          )}
        >
          <rect
            width="32"
            height="32"
            rx="16"
            className={styles.collapseSidebarButtonIconBg}
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M21.7895 20.7855C21.6516 20.9286 21.4624 21.0112 21.2637 21.0149C21.0649 21.0187 20.8728 20.9433 20.7295 20.8055L16.2295 16.5555C16.1569 16.4855 16.0992 16.4017 16.0598 16.3089C16.0203 16.2161 16 16.1163 16 16.0155C16 15.9147 16.0203 15.8149 16.0598 15.7221C16.0992 15.6294 16.1569 15.5455 16.2295 15.4755L20.7295 11.2255C20.7997 11.1538 20.8836 11.0968 20.9762 11.0581C21.0688 11.0194 21.1682 10.9996 21.2686 11C21.369 11.0004 21.4682 11.0209 21.5605 11.0604C21.6528 11.0999 21.7362 11.1575 21.8059 11.2298C21.8755 11.3021 21.9299 11.3876 21.9658 11.4813C22.0018 11.575 22.0186 11.675 22.0152 11.7753C22.0118 11.8756 21.9883 11.9743 21.9461 12.0653C21.9039 12.1564 21.8439 12.2381 21.7695 12.3055L17.8315 16.0155L21.7695 19.7255C21.9127 19.8635 21.9952 20.0526 21.9989 20.2514C22.0027 20.4501 21.9273 20.6423 21.7895 20.7855ZM15.7895 20.7855C15.6516 20.9286 15.4624 21.0112 15.2637 21.0149C15.0649 21.0187 14.8728 20.9433 14.7295 20.8055L10.2295 16.5555C10.1569 16.4855 10.0992 16.4017 10.0598 16.3089C10.0203 16.2161 10 16.1163 10 16.0155C10 15.9147 10.0203 15.8149 10.0598 15.7221C10.0992 15.6294 10.1569 15.5455 10.2295 15.4755L14.7295 11.2255C14.7997 11.1538 14.8836 11.0968 14.9762 11.0581C15.0688 11.0194 15.1682 10.9996 15.2686 11C15.369 11.0004 15.4682 11.0209 15.5605 11.0604C15.6528 11.0999 15.7362 11.1575 15.8059 11.2298C15.8755 11.3021 15.9299 11.3876 15.9658 11.4813C16.0018 11.575 16.0186 11.675 16.0152 11.7753C16.0118 11.8756 15.9883 11.9743 15.9461 12.0653C15.9039 12.1564 15.8439 12.2381 15.7695 12.3055L11.8315 16.0155L15.7695 19.7255C15.9127 19.8635 15.9952 20.0526 15.9989 20.2514C16.0027 20.4501 15.9273 20.6423 15.7895 20.7855Z"
            fill="#B5B4BA"
          />
          <rect
            x="0.5"
            y="0.5"
            width="31"
            height="31"
            rx="15.5"
            strokeOpacity="0.15"
            className={styles.collapseSidebarButtonIconCircle}
          />
        </svg>
      </button>
    </div>
  );
}
