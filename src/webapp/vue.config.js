const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')

const isProd = process.env.NODE_ENV == 'production'

module.exports = {
  assetsDir: 'static',
  configureWebpack: {
    plugins: [
      new webpack.EnvironmentPlugin({
        MELTANO_APP_URL: 'http://localhost:5000',
        DBT_DOCS_URL: 'http://localhost:5000/-/dbt/'
      }),
      new HtmlWebpackPlugin({
        filename: 'index.html',
        injectFlaskContext: isProd,
        template: 'public/index.html'
      })
    ]
  },
  css: {
    loaderOptions: {
      sass: {
        prependData: `
          @import "node_modules/bulma/sass/utilities/initial-variables";
          @import "@/scss/bulma-preset-overrides";
        `
      }
    }
  }
}
