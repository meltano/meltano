module.exports = {
  title: 'Meltano',
  description: 'Open source data dashboarding',
  head: [
    [
      'link',
      {
        rel: 'apple-touch-icon',
        sizes: '180x180',
        href: '/apple-touch-icon.png'
      }
    ],
    [
      'link',
      {
        rel: 'icon',
        type: 'image/png',
        sizes: '32x32',
        href: '/favicon-32x32.png'
      }
    ],
    [
      'link',
      {
        rel: 'icon',
        type: 'image/png',
        sizes: '16x16',
        href: '/favicon-16x16.png'
      }
    ],
    ['link', { rel: 'manifest', href: '/site.webmanifest' }],
    [
      'link',
      {
        rel: 'stylesheet',
        href:
          'https://fonts.googleapis.com/css?family=IBM+Plex+Sans&display=swap'
      }
    ],
    ['meta', { name: 'msapplication-TileColor', content: '#da532c' }],
    ['meta', { name: 'theme-color', content: '#ffffff' }]
  ],
  dest: 'public',
  themeConfig: {
    nav: [
      {
        text: 'Documentation',
        link: '/docs/installation.html'
      },
      { text: 'Blog', link: 'https://www.meltano.com/blog', disableIcon: true },
      {
        text: 'Newsletter',
        link: 'https://meltano.substack.com',
        disableIcon: true
      },
      { text: 'Press', link: '/press/' }
    ],
    sidebar: {
      '/docs': [
        '/docs/',
        '/docs/installation',
        '/docs/getting-started',
        '/tutorials/',
        '/plugins/',
        '/docs/command-line-interface',
        '/docs/environment-variables',
        '/docs/security-and-privacy',
        '/docs/architecture',
        '/docs/contributing',
        '/docs/getting-help',
        '/docs/roadmap'
      ],
      '/plugins': [
        '/docs/',
        '/docs/installation',
        '/docs/getting-started',
        '/tutorials/',
        '/plugins/',
        '/docs/command-line-interface',
        '/docs/environment-variables',
        '/docs/security-and-privacy',
        '/docs/architecture',
        '/docs/contributing',
        '/docs/getting-help',
        '/docs/roadmap'
      ],
      '/tutorials': [
        '/docs/',
        '/docs/installation',
        '/docs/getting-started',
        '/tutorials/',
        '/plugins/',
        '/docs/command-line-interface',
        '/docs/environment-variables',
        '/docs/security-and-privacy',
        '/docs/architecture',
        '/docs/contributing',
        '/docs/getting-help',
        '/docs/roadmap'
      ]
    },
    logo: '/meltano-logo.svg',
    repo: 'https://gitlab.com/meltano/meltano',
    repoLabel: 'Repo',
    lastUpdated: 'Last Updated',
    docsDir: 'src',
    docsRepo: 'https://gitlab.com/meltano/meltano',
    editLinks: true,
    editLinkText: 'Help us improve this page!',
    algolia: {
      apiKey: '6da0449ca46dc108fd88ca828f613ea9',
      indexName: 'meltano'
    },
    data: {
      digitalOceanUrl:
        'https://marketplace.digitalocean.com/apps/meltano?action=deploy&refcode=1c4623f89322'
    }
  },
  plugins: [
    [
      '@vuepress/google-analytics',
      {
        ga: 'UA-132758957-1'
      }
    ],
    [
      'vuepress-plugin-google-tag-manager',
      {
        id: 'GTM-NGTFLR7'
      }
    ],
    ['@vuepress/active-header-links'],
    [require('vuepress-intercom'), { appId: 'ir946q00' }],
    [
      'container',
      {
        type: 'info',
        before: '<div class="custom-block info">',
        after: '</div>'
      }
    ]
  ]
}
