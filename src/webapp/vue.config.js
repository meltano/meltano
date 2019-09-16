const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')

const isProd = process.env.NODE_ENV == 'production'

module.exports = {
  assetsDir: 'static',
  configureWebpack: {
    plugins: [
      new webpack.EnvironmentPlugin({
        AIRFLOW_URL: 'http://localhost:5010',
        MELTANO_WEBAPP_URL: 'http://localhost:5000'
      }),
      new HtmlWebpackPlugin({
        filename: 'index.html',
        injectAnalytics: isProd,
        injectFlaskContext: isProd,
        template: 'public/index.html'
      })
    ]
  }
}
