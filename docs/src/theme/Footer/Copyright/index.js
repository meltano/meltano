import React from 'react';
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
import styles from './copyright.module.scss';

// eslint-disable-next-line react/prop-types
export default function FooterCopyright({ copyright }) {
  return (
    <div className="flex flex-col sm:flex-row justify-between">
      <div
        className="footer__copyright opacity-50 order-2 sm:order-1 text-left"
        // Developer provided the HTML, so assume it's safe.
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: copyright }}
      />
      <div className="footer-soc-wrapper flex justify-between gap-3 order-1 sm:order-2 mb-10 sm:mb-0">
        <a
          href="https://github.com/meltano/meltano"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <GithubLogo title="Github Logo" className={styles.footerSocIcon} />
        </a>
        <a
          href="https://meltano.com/slack"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <SlackLogo title="Slack Logo" className={styles.footerSocIcon} />
        </a>
        <a
          href="https://twitter.com/meltanodata"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <TwitterLogo title="Twitter Logo" className={styles.footerSocIcon} />
        </a>
        <a
          href="https://www.linkedin.com/company/meltano/"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <LinkedinLogo
            title="Linkedin Logo"
            className={styles.footerSocIcon}
          />
        </a>
        {/* <a href="#" className="opacity-50"
          target="_blank">
          <FacebookLogo
            title="Facebook Logo"
            className={styles.footerSocIcon}
          />
        </a>
        <a href="#" className="opacity-50"
          target="_blank">
          <InstagramLogo
            title="Instagram Logo"
            className={styles.footerSocIcon}
          />
        </a> */}
        <a
          href="https://www.youtube.com/meltano"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <YoutubeLogo title="Youtube Logo" className={styles.footerSocIcon} />
        </a>
        <a
          href="https://www.crunchbase.com/organization/meltano"
          className="opacity-50"
          target="_blank" rel="noreferrer"
        >
          <CrunchbaseLogo
            title="Crunchbase Logo"
            className={styles.footerSocIcon}
          />
        </a>
      </div>
    </div>
  );
}
