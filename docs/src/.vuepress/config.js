const docsSidebar = [
  {
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/",
      "/docs/getting-started",
      "/tutorials/",
    ]
  },
  {
    title: "Concepts",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/project",
    ]
  },
  {
    title: "Guide",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/installation",
      "/docs/plugin-management",
      "/docs/configuration",
      "/docs/transforms",
      "/docs/orchestration",
      "/docs/production",
      "/docs/analysis",
    ]
  },
  {
    title: "Reference",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/command-line-interface",
      "/docs/settings",
      "/docs/architecture",
    ]
  },
  {
    title: "More",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/getting-help",
      "/docs/contributor-guide",
      "/docs/responsible-disclosure",
      "/handbook/",
    ]
  }
];

module.exports = {
  title: "Meltano",
  description: "Meltano: Open source ELT",
  head: [
    [
      "link",
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "/apple-touch-icon.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/favicon-32x32.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/favicon-16x16.png",
      },
    ],
    ["link", { rel: "manifest", href: "/site.webmanifest" }],
    [
      "link",
      {
        rel: "stylesheet",
        href:
          "https://fonts.googleapis.com/css?family=IBM+Plex+Sans&display=swap",
      },
    ],
    [
      "meta",
      {
        name: "google-site-verification",
        content: "bOaR0Nxus1Au31YuQX0zMqkNZV_tbAoIr7WkX4crUgI",
      },
    ],
    ["meta", { name: "msapplication-TileColor", content: "#da532c" }],
    ["meta", { name: "theme-color", content: "#ffffff" }],
  ],
  dest: "public",
  themeConfig: {
    nav: [
      {
        text: "Extractors",
        link: "/plugins/extractors/",
      },
      {
        text: "Loaders",
        link: "/plugins/loaders/",
      },
      {
        text: "Documentation",
        link: "/docs/",
      },
      {
        text: "Getting Help",
        link: "/docs/getting-help",
      },
      { text: "Blog", link: "https://www.meltano.com/blog", target: '_self' },
      {
        text: "Join us on Slack",
        link: "https://join.slack.com/t/meltano/shared_invite/zt-cz7s15aq-HXREGBo8Vnu4hEw1pydoRw",
        icon: "SlackIcon"
      },
      {
        text: "Follow us on Twitter",
        link: "https://twitter.com/meltanodata",
        icon: "TwitterIcon"
      },
      {
        text: "View code on GitLab",
        link: "https://gitlab.com/meltano/meltano",
        icon: "GitLabIcon"
      },
      {
        text: "Get started",
        link: "/docs/getting-started.html",
        cta: true
      }
    ],
    sidebar: {
      "/docs": docsSidebar,
      "/tutorials": docsSidebar,
      "/handbook/engineering/meltanodata-guide": [
        "/handbook/engineering/meltanodata-guide/",
        "/handbook/engineering/meltanodata-guide/controller-node",
      ],
      "/handbook": [
        "/handbook/",
        "/handbook/engineering/",
        "/handbook/marketing/",
        "/handbook/product/",
      ],
    },
    logo: "/meltano-logo-with-text.svg",
    lastUpdated: "Last Updated",
    docsDir: "src",
    docsRepo: "https://gitlab.com/meltano/meltano",
    editLinks: true,
    editLinkText: "Help us improve this page!",
    algolia: {
      apiKey: "6da0449ca46dc108fd88ca828f613ea9",
      indexName: "meltano",
    },
    data: {
      digitalOceanUrl:
        "https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322",
      slackChannelUrl:
        "https://join.slack.com/t/meltano/shared_invite/zt-cz7s15aq-HXREGBo8Vnu4hEw1pydoRw",
    },
    smoothScroll: true
  },
  plugins: [
    [
      "@vuepress/google-analytics",
      {
        ga: "UA-132758957-1",
      },
    ],
    [
      "vuepress-plugin-google-tag-manager",
      {
        id: "GTM-NGTFLR7",
      },
    ],
    ["@vuepress/active-header-links"],
    [require("vuepress-intercom"), { appId: "ir946q00" }],
    [
      "container",
      {
        type: "info",
        before: '<div class="custom-block info">',
        after: "</div>",
      },
    ],
    [
      "vuepress-plugin-sitemap",
      {
        hostname: "https://meltano.com",
      },
    ],
  ],
};
