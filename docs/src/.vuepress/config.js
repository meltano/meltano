module.exports = {
  title: 'Meltano',
  description: 'Open source data dashboarding software',
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
    ['meta', { name: 'msapplication-TileColor', content: '#da532c' }],
    ['meta', { name: 'theme-color', content: '#ffffff' }],
  ],
  dest: 'public',
  themeConfig: {
    nav: [
      { text: 'Documentation', link: '/docs/' },
      { text: 'Blog', link: 'https://www.meltano.com/blog', disableIcon: true },
      { text: 'Newsletter', link: 'https://docs.google.com/forms/d/e/1FAIpQLSdyiKeMwO2qB4hJZnjBhVExBZwPATgz6_QTJjXKLiTNPmhW9w/viewform?usp=sf_link' },
      { text: 'Press', link: '/press/' }
    ],
    sidebar: {
      '/docs': [
        '/docs/',
        '/docs/installation',
        '/docs/quickstart',
        '/docs/tutorial',
        '/docs/meltano-cli',
        '/docs/plugins',
        '/docs/environment-variables',
        '/docs/security-and-privacy',
        '/docs/deployment',
        '/docs/roadmap',
        '/docs/architecture',
        '/docs/contributing'
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
    }
  },
  plugins: [
    [
      '@vuepress/google-analytics',
      {
        ga: 'UA-132758957-1'
      }
    ]
  ]
}
