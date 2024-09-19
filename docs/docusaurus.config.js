/* eslint-disable no-undef */
// @ts-nocheck
// Note: type annotations allow type checking and IDEs autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Meltano Documentation',
  tagline: '',
  url: 'https://docs.meltano.com',
  baseUrl: '/',
  onBrokenLinks: 'log',
  onBrokenMarkdownLinks: 'log',
  favicon: 'img/favicon.png',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  plugins: ['docusaurus-plugin-sass'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: 'https://github.com/meltano/meltano/blob/main/docs',
        },
        blog: {
          routeBasePath: '/changelog',
          blogTitle: 'Changelog',
          blogSidebarTitle: 'All Releases',
          blogDescription: '',
          postsPerPage: 5,
          showReadingTime: false,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      // announcementBar: {
      //   id: 'meltano_docs_announcment',
      //   content: '<a href="https://meltano.com/blog/introducing-meltano-cloud-you-build-the-pipelines-we-manage-the-infrastructure/">⚡ Meltano Cloud is now in Public Beta: you define the pipeline, we manage the infra. Sign up now and claim your 100 free credits! ⚡</a>',
      //   backgroundColor: '#311772',
      //   textColor: '#F5F7FA',
      //   isCloseable: true,
      // },
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: '| Docs',
        logo: {
          alt: 'Purple dragon with the meltano wordmark',
          src: 'img/meltano.svg',
        },
        items: [
          {
            type: 'search',
            position: 'right',
          },
          {
            to: '/getting-started/installation/',
            label: 'Get Started',
            position: 'left',
            className: 'header-get-started-link',
            'aria-label': 'Get Started',
          },
          {
            to: '/tutorials',
            label: 'Tutorials',
            position: 'left',
            className: 'header-tutorials-link',
            'aria-label': 'Tutorials',
          },
          {
            to: '/getting-started/',
            label: 'Docs',
            position: 'left',
            className: 'header-docs-link',
            'aria-label': 'Docs',
          },
          {
            to: '/changelog',
            label: 'Changelog',
            position: 'left',
            className: 'header-changelog-link',
            'aria-label': 'Changelog',
          },
          {
            href: 'https://github.com/meltano/meltano',
            label: ' ',
            position: 'right',
            className: 'header-github-link',
            'aria-label': 'GitHub repository',
          },
          {
            href: 'https://meltano.com/slack',
            label: ' ',
            position: 'right',
            className: 'header-slack-link',
            'aria-label': 'Slack community',
          },
        ],
      },
      footer: {
        style: 'light',
        links: [
          {
            title: 'The Project',
            items: [
              {
                label: 'Our Mission',
                to: 'https://handbook.meltano.com/company/#mission',
              },
              {
                label: 'Our Vision',
                to: 'https://handbook.meltano.com/company/#vision',
              },
              {
                label: 'Roadmap',
                to: 'https://handbook.meltano.com/product/roadmap',
              },
              {
                label: 'Strategy',
                to: 'https://handbook.meltano.com/company/#strategy',
              },
            ],
          },
          {
            title: 'Company',
            items: [
              {
                label: 'Handbook',
                href: 'https://handbook.meltano.com/',
              },
              {
                label: 'Values',
                href: 'https://handbook.meltano.com/company/values',
              },
              {
                label: 'History',
                href: 'https://handbook.meltano.com/timeline',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Slack',
                href: 'https://meltano.com/slack',
              },
              {
                label: 'MeltanoLabs',
                href: 'https://github.com/MeltanoLabs',
              },
              {
                label: 'Meltano Hub',
                href: 'https://hub.meltano.com/',
              },
            ],
          },
          {
            title: 'Get Help',
            items: [
              {
                label: 'Contact',
                href: 'https://meltano.com/slack',
              },
              {
                label: 'StackOverflow',
                href: 'https://stackoverflow.com/questions/tagged/meltano',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Arch Data, Inc.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['yaml', 'json', 'bash'],
      },
      docs: {
        sidebar: {
          hideable: true,
        },
      },
      // https://www.docusaurus.io/docs/search
      algolia: {
        appId: 'RH6DR0I7R7',
        apiKey: '6d3c8732a3b6feb9fdae6de7b68de90e',
        indexName: 'meltanodocs',
        // contextualSearch: true,
        // searchParameters: {},
        // searchPagePath: "search",
      },
    }),
};

module.exports = config;
