module.exports = {
	title: 'Meltano',
	description: 'From data source to dashboard',
	head: [
		['link', { rel: "apple-touch-icon", sizes: "180x180", href: "/apple-touch-icon.png" }],
		['link', { rel: "icon", type: "image/png", sizes: "32x32", href: "/favicon-32x32.png" }],
		['link', { rel: "icon", type: "image/png", sizes: "16x16", href: "/favicon-16x16.png" }],
		['link', { rel: "manifest", href: "/site.webmanifest" }],
		['meta', { name: "msapplication-TileColor", content: "#da532c" }],
		['meta', { name: "theme-color", content: "#ffffff" }]
	],
	dest: './docs/public',
	themeConfig: {
		nav: [
			{ text: 'Home', link: '/' },
			{ 
				text: 'Learn',
				items: [
					{ text: 'Getting Started', link: '/guide/' },
					{ text: 'Tutorial', link: '/guide/tutorial' },
					{ text: 'Fundamentals', link: '/guide/fundamentals' },
					{ text: 'Best Practices', link :'/guide/best-practices' }
				]
			},
			{ text: 'Documentation', link: '/docs/' },
			{ text: 'About', link: '/about/' }
		],
		sidebar: {
			'/docs': [
				'/docs/',
				'/docs/source-to-dashboard',
				'/docs/version-control',
				'/docs/taps-targets',
				'/docs/security-privacy',
				'/docs/license',
				'/docs/release',
				'/docs/contributing'
			]
		},
		repo: 'https://gitlab.com/meltano/meltano',
		repoLabel: 'Repo',
		lastUpdated: 'Last Updated',
		docsDir: 'src',
		docsRepo: 'https://gitlab.com/meltano/meltano',
		editLinks: true,
		editLinkText: 'Help us improve this page!'
	}
}
