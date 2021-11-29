const docsSidebar = [
  {
    collapsable: false,
    sidebarDepth: 2,
    children: ["/docs/", "/docs/getting-started", "/tutorials/"],
  },
  {
    title: "Concepts",
    collapsable: false,
    sidebarDepth: 2,
    children: ["/docs/project", "/docs/plugins", "/docs/environments"],
  },
  {
    title: "Guide",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/installation",
      "/docs/plugin-management",
      "/docs/configuration",
      "/docs/integration",
      "/docs/transforms",
      "/docs/orchestration",
      "/docs/containerization",
      "/docs/production",
      "/docs/analysis",
      "/docs/ui",
    ],
  },
  {
    title: "Reference",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/command-line-interface",
      "/docs/settings",
      "/docs/architecture",
      ["https://hub.meltano.com/singer/spec", "Singer Spec"],
    ],
  },
  {
    title: "The Project",
    collapsable: false,
    sidebarDepth: 2,
    children: [
      "/docs/getting-help",
      "/docs/community",
      "/docs/contributor-guide",
      "/docs/responsible-disclosure",
      ["https://handbook.meltano.com/", "Company Handbook"],
    ],
  },
];

module.exports = {
  title: "Meltano",
  description: "Meltano: ELT for the DataOps era",
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
        text: "Connectors",
        items: [
          {
            text: "Sources",
            link: "https://hub.meltano.com/extractors/",
          },
          {
            text: "Destinations",
            link: "https://hub.meltano.com/loaders/",
          },
          {
            text: "Connector SDK",
            link: "https://sdk.meltano.com/",
          },
          {
            text: "Implementation Partners",
            link: "/partners/",
          },
        ],
      },
      {
        text: "Docs",
        link: "/docs/",
      },
      {
        text: "Getting Help",
        items: [
          {
            text: "Issue Tracker",
            link: "https://gitlab.com/meltano/meltano/issues",
          },
          {
            text: "Slack",
            link: "https://meltano.com/slack",
          },
          {
            text: "Office Hours",
            link: "/docs/community#office-hours",
          },
        ],
      },
      {
        text: "Community",
        items: [
          {
            text: "Guidelines",
            link: "/docs/community#guidelines",
          },
          {
            text: "Office Hours",
            link: "/docs/community#office-hours",
          },
          {
            text: "Demo Days",
            link: "/docs/community#demo-days",
          },
          {
            text: "Contributing",
            link: "/docs/contributor-guide.html",
          },
          {
            text: "Slack",
            link: "https://meltano.com/slack",
          },
          {
            text: "YouTube",
            link: "https://www.youtube.com/meltano",
          },
        ],
      },
      {
        text: "Company",
        items: [
          {
            text: "About",
            link: "https://handbook.meltano.com/company/",
          },
          {
            text: "Jobs",
            link: "/jobs/",
          },
          {
            text: "Team",
            link: "/team/",
          },
          {
            text: "Values",
            link: "https://handbook.meltano.com/company/values",
          },
          {
            text: "Handbook",
            link: "https://handbook.meltano.com",
          },
          {
            text: "Press",
            link: "/press/",
          },
        ],
      },
      { text: "Blog", link: "https://www.meltano.com/blog", target: "_self" },
      {
        text: "Join 1900+ on Slack",
        link: "https://meltano.com/slack",
        icon: "SlackIcon",
      },
      {
        text: "Follow us on Twitter",
        link: "https://twitter.com/meltanodata",
        icon: "TwitterIcon",
      },
      {
        text: "Contribute on GitLab",
        link: "https://gitlab.com/meltano/meltano",
        icon: "GitLabIcon",
      },
      {
        text: "Watch on YouTube",
        link: "https://www.youtube.com/meltano",
        icon: "YouTubeIcon",
      },
      {
        text: "Get started",
        link: "/docs/getting-started.html",
        cta: true,
      },
    ],
    sidebar: {
      "/docs": docsSidebar,
      "/tutorials": docsSidebar,
    },
    logo: "/meltano-logo-with-text.svg",
    lastUpdated: "Last Updated",
    docsDir: "docs/src",
    docsRepo: "https://gitlab.com/meltano/meltano",
    editLinks: true,
    editLinkText: "View page source in repository",
    algolia: {
      apiKey: "6da0449ca46dc108fd88ca828f613ea9",
      indexName: "meltano",
    },
    data: {
      digitalOceanUrl:
        "https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322",
      slackChannelUrl: "https://meltano.com/slack",
    },
    smoothScroll: true,
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
