import React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { ThemeClassNames } from '@docusaurus/theme-common';
import { isActiveSidebarItem } from '@docusaurus/plugin-content-docs/client';
import Link from '@docusaurus/Link';
import isInternalUrl from '@docusaurus/isInternalUrl';
import IconExternalLink from '@theme/Icon/ExternalLink';
import styles from './styles.module.css';

const ICONS = {
  cloud: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M4.99959 8C4.99959 7.0111 5.29283 6.0444 5.84224 5.22215C6.39165 4.39991 7.17254 3.75904 8.08617 3.3806C8.9998 3.00217 10.0051 2.90315 10.975 3.09608C11.9449 3.289 12.8359 3.76521 13.5351 4.46447C14.2344 5.16373 14.7106 6.05465 14.9035 7.02455C15.0964 7.99446 14.9974 8.99979 14.619 9.91342C14.2405 10.827 13.5997 11.6079 12.7774 12.1573C11.9552 12.7068 10.9885 13 9.99959 13H4.49959C4.00331 12.9994 3.51284 12.8932 3.06072 12.6886C2.6086 12.484 2.20516 12.1855 1.87718 11.8131C1.54921 11.4406 1.30418 11.0027 1.15838 10.5283C1.01257 10.0539 0.96931 9.55399 1.03147 9.06162C1.09363 8.56925 1.25979 8.09573 1.51892 7.67248C1.77805 7.24923 2.12422 6.88593 2.53448 6.60668C2.94473 6.32743 3.40968 6.13861 3.89848 6.05277C4.38727 5.96692 4.88873 5.986 5.36959 6.10875"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  bell: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M9 14H7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 6.875C8.34518 6.875 8.625 6.59518 8.625 6.25C8.625 5.90482 8.34518 5.625 8 5.625C7.65482 5.625 7.375 5.90482 7.375 6.25C7.375 6.59518 7.65482 6.875 8 6.875Z"
        fill="currentColor"
      />
      <path
        d="M5.9258 12C2.34518 5.95751 6.49205 2.03313 7.6933 1.10501C7.78105 1.03679 7.88903 0.999756 8.00018 0.999756C8.11133 0.999756 8.2193 1.03679 8.30705 1.10501C9.5083 2.03313 13.6552 5.95751 10.0746 12H5.9258Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M11.4898 6.92999L13.3842 9.20249C13.4331 9.26127 13.4679 9.33048 13.4859 9.40481C13.5039 9.47914 13.5046 9.5566 13.488 9.63124L12.7155 13.1081C12.6971 13.191 12.6578 13.2679 12.6015 13.3314C12.5451 13.395 12.4735 13.4431 12.3934 13.4713C12.3133 13.4995 12.2273 13.5069 12.1436 13.4926C12.0599 13.4784 11.9811 13.4431 11.9148 13.39L10.0742 12"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M4.51011 6.92999L2.61574 9.20249C2.56681 9.26127 2.53201 9.33048 2.51403 9.40481C2.49604 9.47914 2.49534 9.5566 2.51199 9.63124L3.28449 13.1081C3.30291 13.191 3.34214 13.2679 3.39849 13.3314C3.45483 13.395 3.52644 13.4431 3.60655 13.4713C3.68666 13.4995 3.77263 13.5069 3.85636 13.4926C3.94009 13.4784 4.01882 13.4431 4.08511 13.39L5.92574 12"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  download: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M8 9V2"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M13.5 9V13H2.5V9"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M10.5 6.5L8 9L5.5 6.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  connect: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M9 4L11.5 1.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14.5 4.5L12 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14 9L7 2"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M13.25 8.25L9.58564 11.9144C9.21057 12.2894 8.70193 12.5 8.17157 12.5C7.64121 12.5 7.13257 12.2894 6.75751 11.9144L4.08564 9.2425C3.71066 8.86744 3.5 8.3588 3.5 7.82844C3.5 7.29808 3.71066 6.78944 4.08564 6.41437L7.75001 2.75"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M5.42188 10.5781L2 14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  database: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M8 8C11.0376 8 13.5 6.65685 13.5 5C13.5 3.34315 11.0376 2 8 2C4.96243 2 2.5 3.34315 2.5 5C2.5 6.65685 4.96243 8 8 8Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M2.5 5V8C2.5 9.65688 4.9625 11 8 11C11.0375 11 13.5 9.65688 13.5 8V5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M2.5 8V11C2.5 12.6569 4.9625 14 8 14C11.0375 14 13.5 12.6569 13.5 11V8"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  process: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7.39062 6.62936L6.60938 4.87061"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M11.0756 6.97437L9.42188 7.52562"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M11.3161 10.5794L9.18359 8.92065"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6.87859 8.99628L4.62109 11.0038"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 9.5C8.82843 9.5 9.5 8.82843 9.5 8C9.5 7.17157 8.82843 6.5 8 6.5C7.17157 6.5 6.5 7.17157 6.5 8C6.5 8.82843 7.17157 9.5 8 9.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6 5C6.82843 5 7.5 4.32843 7.5 3.5C7.5 2.67157 6.82843 2 6 2C5.17157 2 4.5 2.67157 4.5 3.5C4.5 4.32843 5.17157 5 6 5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12.5 8C13.3284 8 14 7.32843 14 6.5C14 5.67157 13.3284 5 12.5 5C11.6716 5 11 5.67157 11 6.5C11 7.32843 11.6716 8 12.5 8Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12.5 13C13.3284 13 14 12.3284 14 11.5C14 10.6716 13.3284 10 12.5 10C11.6716 10 11 10.6716 11 11.5C11 12.3284 11.6716 13 12.5 13Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M3.5 13.5C4.32843 13.5 5 12.8284 5 12C5 11.1716 4.32843 10.5 3.5 10.5C2.67157 10.5 2 11.1716 2 12C2 12.8284 2.67157 13.5 3.5 13.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  code: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M8 14C11.3137 14 14 11.3137 14 8C14 4.68629 11.3137 2 8 2C4.68629 2 2 4.68629 2 8C2 11.3137 4.68629 14 8 14Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 14C11.3137 14 14 11.3137 14 8C14 4.68629 11.3137 2 8 2C4.68629 2 2 4.68629 2 8C2 11.3137 4.68629 14 8 14Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7 8.73248C6.61872 8.51234 6.32073 8.17255 6.15224 7.76579C5.98376 7.35904 5.9542 6.90806 6.06815 6.48279C6.1821 6.05752 6.43319 5.68174 6.78248 5.41372C7.13177 5.1457 7.55973 5.00043 8 5.00043C8.44027 5.00043 8.86824 5.1457 9.21752 5.41372C9.56681 5.68174 9.8179 6.05752 9.93185 6.48279C10.0458 6.90806 10.0162 7.35904 9.84776 7.76579C9.67928 8.17255 9.38128 8.51234 9 8.73248L10 11H6L7 8.73248Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  server: (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M5 6L7.5 8L5 10"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8.5 10H11"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M13.5 3H2.5C2.22386 3 2 3.22386 2 3.5V12.5C2 12.7761 2.22386 13 2.5 13H13.5C13.7761 13 14 12.7761 14 12.5V3.5C14 3.22386 13.7761 3 13.5 3Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
};

const BADGE_CONFIG = {
  cloud: { label: 'Cloud', className: styles.badgeCloud },
  community: { label: 'Community', className: styles.badgeCommunity },
  open: { label: 'Open', className: styles.badgeOpen },
};

export default function DocSidebarItemLink({
  item,
  onItemClick,
  activePath,
  level,
  index,
  ...props
}) {
  const { href, label, className, autoAddBaseUrl, customProps } = item;
  const isActive = isActiveSidebarItem(item, activePath);
  const isInternalLink = isInternalUrl(href);

  const icon = customProps?.icon;
  const badgeType = customProps?.badgeType;
  const badgeConfig = badgeType ? BADGE_CONFIG[badgeType] : null;

  if (customProps?.hide_from_sidebar) {
    return null;
  }

  return (
    <li
      className={clsx(
        ThemeClassNames.docs.docSidebarItemLink,
        ThemeClassNames.docs.docSidebarItemLinkLevel(level),
        'menu__list-item',
        className,
      )}
    >
      <Link
        className={clsx('menu__link', styles.menuLink, {
          'menu__link--active': isActive,
        })}
        autoAddBaseUrl={autoAddBaseUrl}
        aria-current={isActive ? 'page' : undefined}
        to={href}
        {...(isInternalLink && {
          onClick: onItemClick ? () => onItemClick(item) : undefined,
        })}
        {...props}
      >
        {icon && ICONS[icon] && (
          <span
            className={clsx(styles.icon, { [styles.iconActive]: isActive })}
          >
            {ICONS[icon]}
          </span>
        )}
        <span className={styles.labelGroup}>
          <span className={styles.label}>{label}</span>
          {badgeConfig && (
            <span className={clsx(styles.badge, badgeConfig.className)}>
              {badgeConfig.label}
            </span>
          )}
        </span>
        {!isInternalLink && <IconExternalLink />}
      </Link>
    </li>
  );
}

DocSidebarItemLink.propTypes = {
  item: PropTypes.shape({
    href: PropTypes.string,
    label: PropTypes.string,
    className: PropTypes.string,
    autoAddBaseUrl: PropTypes.bool,
    customProps: PropTypes.shape({
      icon: PropTypes.string,
      badgeType: PropTypes.string,
      hide_from_sidebar: PropTypes.bool,
    }),
  }).isRequired,
  onItemClick: PropTypes.func,
  activePath: PropTypes.string.isRequired,
  level: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};
