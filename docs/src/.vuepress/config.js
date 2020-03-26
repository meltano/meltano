const docsSidebar = [
  "/docs/",
  "/docs/getting-started",
  "/docs/data-sources",
  "/docs/getting-help",
  "/docs/responsible-disclosure",
  "/developer-tools/",
  "/handbook/"
];

const devToolsSidebar = [
  "/developer-tools/",
  "/developer-tools/self-hosted-installation.html",
  "/developer-tools/command-line-interface.html",
  "/developer-tools/environment-variables.html",
  "/plugins/extractors/",
  "/plugins/loaders/",
  "/tutorials/",
  "/developer-tools/orchestration.html",
  "/developer-tools/transforms.html",
  "/developer-tools/role-based-access-control.html",
  "/developer-tools/contributor-guide.html",
  "/developer-tools/architecture.html"
];

module.exports = {
  title: "Meltano",
  description: "Open source data dashboarding",
  head: [
    [
      "link",
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "/apple-touch-icon.png"
      }
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/favicon-32x32.png"
      }
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/favicon-16x16.png"
      }
    ],
    ["link", { rel: "manifest", href: "/site.webmanifest" }],
    [
      "link",
      {
        rel: "stylesheet",
        href:
          "https://fonts.googleapis.com/css?family=IBM+Plex+Sans&display=swap"
      }
    ],
    [
      "meta",
      {
        name: "google-site-verification",
        content: "bOaR0Nxus1Au31YuQX0zMqkNZV_tbAoIr7WkX4crUgI"
      }
    ],
    ["meta", { name: "msapplication-TileColor", content: "#da532c" }],
    ["meta", { name: "theme-color", content: "#ffffff" }]
  ],
  dest: "public",
  themeConfig: {
    nav: [
      {
        text: "Getting Started",
        link: "/docs/getting-started.html"
      },
      {
        text: "Developer Tools",
        link: "/developer-tools/"
      },
      { text: "Blog", link: "https://www.meltano.com/blog", disableIcon: true },
      {
        text: "Newsletter",
        link: "https://meltano.substack.com",
        disableIcon: true
      }
    ],
    sidebar: {
      "/docs": docsSidebar,
      "/developer-tools": devToolsSidebar,
      "/tutorials": devToolsSidebar,
      "/plugins": devToolsSidebar,
      "/handbook/engineering/meltanodata-guide": [
        "/handbook/engineering/meltanodata-guide/",
        "/handbook/engineering/meltanodata-guide/controller-node.html"
      ],
      "/handbook": [
        "/handbook/",
        "/handbook/engineering/",
        "/handbook/marketing/",
        "/handbook/product/"
      ]
    },
    logo: "/meltano-logo.svg",
    repo: "https://gitlab.com/meltano/meltano",
    repoLabel: "Repo",
    lastUpdated: "Last Updated",
    docsDir: "src",
    docsRepo: "https://gitlab.com/meltano/meltano",
    editLinks: true,
    editLinkText: "Help us improve this page!",
    algolia: {
      apiKey: "6da0449ca46dc108fd88ca828f613ea9",
      indexName: "meltano"
    },
    data: {
      digitalOceanUrl:
        "https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322",
      slackChannelUrl:
        "https://join.slack.com/t/meltano/shared_invite/zt-cz7s15aq-HXREGBo8Vnu4hEw1pydoRw"
    }
  },
  plugins: [
    [
      "@vuepress/google-analytics",
      {
        ga: "UA-132758957-1"
      }
    ],
    [
      "vuepress-plugin-google-tag-manager",
      {
        id: "GTM-NGTFLR7"
      }
    ],
    ["@vuepress/active-header-links"],
    [require("vuepress-intercom"), { appId: "ir946q00" }],
    [
      "container",
      {
        type: "info",
        before: '<div class="custom-block info">',
        after: "</div>"
      }
    ],
    [
      "vuepress-plugin-sitemap",
      {
        hostname: "https://meltano.com"
      }
    ]
  ]
};
