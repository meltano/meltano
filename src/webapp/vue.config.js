const webpack = require('webpack')
const isProd = process.env.NODE_ENV == 'production'

module.exports = {
  assetsDir: 'static',

  // add another entry point to the webpack configuration
  pages: {
    app: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      chunks: ['chunk-vendors', 'chunk-common', 'app'],

      // forwarded to html-webpack-plugin
      injectFlaskContext: isProd,
    },
    embed: {
      entry: 'src/main-embed.js',
      template: 'public/index.html',
      filename: 'index-embed.html',
      chunks: ['chunk-vendors', 'chunk-common', 'embed'],

      // forwarded to html-webpack-plugin
      injectFlaskContext: isProd,
    },
  },

  devServer: {
    historyApiFallback: {
      verbose: true,
      index:
        process.env.MELTANO_EMBED == '1' ? '/index-embed.html' : '/index.html',
    },
  },

  configureWebpack: {
    plugins: [
      new webpack.EnvironmentPlugin({
        MELTANO_APP_URL: 'http://localhost:5000',
        MELTANO_OAUTH_SERVICE_URL: 'http://localhost:5000/-/oauth',
        MELTANO_OAUTH_SERVICE_PROVIDERS: 'all',
        MELTANO_UI_NOTIFICATION: 'False',
      }),
    ],
  },

  css: {
    loaderOptions: {
      sass: {
        prependData: `
          @import "node_modules/bulma/sass/utilities/initial-variables";
          @import "@/scss/bulma-preset-overrides";
        `,
      },
    },
  },
}
