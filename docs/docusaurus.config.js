
// @ts-nocheck
// Note: type annotations allow type checking and IDEs autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.oneLight;
const darkCodeTheme = themes.oneDark;
const isProd = process.env.NODE_ENV === 'production';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Meltano Documentation',
  tagline: '',
  url: 'https://docs.meltano.com',
  baseUrl: '/',
  trailingSlash: false,
  onBrokenLinks: 'throw',
  onBrokenAnchors: 'warn',
  favicon: 'img/favicon.png',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

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
          postsPerPage: 20,
          blogSidebarCount: 'ALL',
          showReadingTime: false,
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        ...(isProd && {
          gtag: {
            trackingID: ['G-Z3RR2S48WN'],
          },
        }),
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
      //   id: 'meltano_docs_announcement',
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
            to: '/getting-started/which-meltano',
            label: 'Platform',
            position: 'left',
            className: 'header-platform-link',
            'aria-label': 'Platform',
            activeBaseRegex: '^/(getting-started|meltano-cloud|meltano-open|guide|concepts|reference|tutorials|contribute)(/|$)',
          },
          {
            to: '/connectors',
            label: 'Connectors',
            position: 'left',
            className: 'header-connectors-link',
            'aria-label': 'Connectors',
            activeBasePath: '/connectors',
          },
          {
            to: '/changelog',
            label: 'Changelog',
            position: 'left',
            className: 'header-changelog-link',
            'aria-label': 'Changelog',
            activeBasePath: '/changelog',
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
            title: 'Meltano',
            items: [
              {
                label: 'Overview',
                href: 'https://meltano.com/product',
              },
              {
                label: 'Blogs',
                href: 'https://meltano.com/blog',
              },
              {
                label: 'Case studies',
                href: 'https://meltano.com/case-studies',
              },
              {
                label: 'Data Matas Podcast',
                href: 'https://meltano.com/podcasts',
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
        copyright: `Copyright © ${new Date().getFullYear()} Matatika Limited.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['yaml', 'json', 'bash', 'toml'],
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
