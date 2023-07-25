import React from 'react';
import GithubLogo from '@site/static/img/footer/github.svg';
import Translate from '@docusaurus/Translate';
import clsx from 'clsx';
import { ThemeClassNames } from '@docusaurus/theme-common';
import styles from './editthispage.module.scss';

// eslint-disable-next-line react/prop-types
export default function EditThisPage({ editUrl }) {
  return (
    <a
      href={editUrl}
      target="_blank"
      rel="noreferrer noopener"
      className={clsx(ThemeClassNames.common.editThisPage, styles.editThisPage)}
    >
      <GithubLogo
        title="Github Logo"
        className={clsx('inline mr-2 mb-1', styles.githubIcon)}
      />
      <Translate
        id="theme.common.editThisPage"
        description="The link label to edit the current page"
      >
        Edit this page on Github
      </Translate>
    </a>
  );
}
