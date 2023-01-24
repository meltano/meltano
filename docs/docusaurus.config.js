// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Meltano',
  tagline: 'Meltano Documentation',
  url: 'https://docs.meltano.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'meltano', // Usually your GitHub org/user name.
  projectName: 'meltano', // Usually your repo name.

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  plugins: [
    [
      "docusaurus-plugin-remote-content",
      {
          // options here
          name: "latest-changelog", // used by CLI, must be path safe
          sourceBaseUrl: "https://raw.githubusercontent.com/meltano/meltano/main/", // the base url for the markdown (gets prepended to all of the documents when fetching)
          outDir: "src/pages/", // the base directory to output to.
          documents: ["CHANGELOG.md"], // the file names to download
          performCleanup: false,
      },
    ],
  ],

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
          editUrl:
            'https://github.com/meltano/meltano',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Meltano Documentation',
        logo: {
          alt: 'Purple dragon with the meltano wordmark',
          src: 'img/meltano-logo-padded.svg',
        },
        items: [
          {to: '#', label: 'Getting Started', position: 'left'},
          {to: '#', label: 'Guides', position: 'left'},
          {to: '#', label: 'Concepts', position: 'left'},
          {to: '#', label: 'Tutorials', position: 'left'},
          {to: '#', label: 'Reference', position: 'left'},
          {to: '#', label: 'Contribute', position: 'left'},
          {
            type: 'docsVersionDropdown',
          },
          {
            href: 'https://github.com/meltano/meltano',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
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
        copyright: `Copyright © ${new Date().getFullYear()} Meltano.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
      algolia: {
        // The application ID provided by Algolia
        appId: 'YOUR_APP_ID',

        // Public API key: it is safe to commit it
        apiKey: 'YOUR_SEARCH_API_KEY',

        indexName: 'YOUR_INDEX_NAME',

        // Optional: see doc section below
        contextualSearch: true,

        // Optional: Specify domains where the navigation should occur through window.location instead on history.push. Useful when our Algolia config crawls multiple documentation sites and we want to navigate with window.location.href to them.
        externalUrlRegex: 'external\\.com|domain\\.com',

        // Optional: Algolia search parameters
        searchParameters: {},

        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: 'search',

        //... other Algolia params
      },
      announcementBar: {
        id: 'announcementBar',
        content: "This is an announcement. <a href='#' style='color: #fbbf52; font-weight: bold;'>Call to action!</a>",
        backgroundColor: '#031d4d',
        textColor: '#ffffff',
        isCloseable: true,
      },
    }),
};

module.exports = config;
