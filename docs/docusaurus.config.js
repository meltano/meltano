/* eslint-disable no-undef */
// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require("prism-react-renderer/themes/github");
const darkCodeTheme = require("prism-react-renderer/themes/oceanicNext");

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Meltano",
  tagline: "Meltano Documentation",
  url: "https://docs.meltano.com",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  plugins: ["docusaurus-plugin-sass"],

  presets: [
    [
      "classic",
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: "/",
          sidebarPath: require.resolve("./sidebars.js"),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: "https://github.com/meltano/meltano",
        },
        blog: {
          // showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            "https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/",
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: "light",
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      announcementBar: {
        id: "meltano_docs_announcment",
        content: `<a href="#">⚡ New Release: Meltano Runbooks are now better than ever with conditions ⚡</a>`,
        backgroundColor: "#311772",
        textColor: "#F5F7FA",
        isCloseable: false,
      },
      // Replace with your project's social card
      image: "img/docusaurus-social-card.jpg",
      navbar: {
        title: "| Docs",
        logo: {
          alt: "Purple dragon with the meltano wordmark",
          src: "img/meltano.svg",
        },
        items: [
          {
            type: "search",
            position: "right",
          },
          {
            to: "/intro",
            label: "Get Started",
            position: "left",
            className: "header-get-started-link",
            "aria-label": "Get Started",
          },
          {
            to: "/intro",
            label: "Tutorials",
            position: "left",
            className: "header-tutorials-link",
            "aria-label": "Tutorials",
          },
          {
            to: "/intro",
            label: "Docs",
            position: "left",
            className: "header-docs-link",
            "aria-label": "Docs",
          },
          {
            to: "/blog",
            label: "Changelog",
            position: "left",
            className: "header-changelog-link",
            "aria-label": "Changelog",
          },
          // {
          //   type: "docsVersionDropdown",
          // },
          {
            href: "https://github.com/facebook/docusaurus",
            label: " ",
            position: "right",
            className: "header-github-link",
            "aria-label": "GitHub repository",
          },
          {
            href: "https://github.com/facebook/docusaurus",
            label: " ",
            position: "right",
            className: "header-slack-link",
            "aria-label": "Slack community",
          },
        ],
      },
      footer: {
        style: "light",
        links: [
          {
            title: "The Project",
            items: [
              {
                label: "Our Mission",
                to: "https://handbook.meltano.com/company/#mission",
              },
              {
                label: "Our Vision",
                to: "https://handbook.meltano.com/company/#vision",
              },
              {
                label: "Roadmap",
                to: "https://handbook.meltano.com/product/roadmap",
              },
              {
                label: "Strategy",
                to: "https://handbook.meltano.com/company/#strategy",
              },
            ],
          },
          {
            title: "Company",
            items: [
              {
                label: "Handbook",
                href: "https://handbook.meltano.com/",
              },
              {
                label: "Values",
                href: "https://handbook.meltano.com/company/values",
              },
              {
                label: "History",
                href: "https://handbook.meltano.com/timeline",
              },
            ],
          },
          {
            title: "Community",
            items: [
              {
                label: "Slack",
                href: "https://meltano.com/slack",
              },
              {
                label: "MeltanoLabs",
                href: "https://github.com/MeltanoLabs",
              },
              {
                label: "Meltano Hub",
                href: "https://hub.meltano.com/",
              },
            ],
          },
          {
            title: "Get Help",
            items: [
              {
                label: "Contact",
                href: "https://meltano.com/slack",
              },
              {
                label: "StackOverflow",
                href: "https://stackoverflow.com/questions/tagged/meltano",
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
      docs: {
        sidebar: {
          hideable: true,
        },
      },
      algolia: {
        // The application ID provided by Algolia
        appId: "YOUR_APP_ID",

        // Public API key: it is safe to commit it
        apiKey: "YOUR_SEARCH_API_KEY",

        indexName: "YOUR_INDEX_NAME",

        // Optional: see doc section below
        contextualSearch: true,

        // Optional: Specify domains where the navigation should occur through window.location instead on history.push. Useful when our Algolia config crawls multiple documentation sites and we want to navigate with window.location.href to them.
        externalUrlRegex: "external\\.com|domain\\.com",

        // Optional: Algolia search parameters
        searchParameters: {},

        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: "search",

        //... other Algolia params
      },
    }),
};

module.exports = config;
