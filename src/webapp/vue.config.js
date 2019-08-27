const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  assetsDir: 'static',
  configureWebpack: {
    plugins: [
      new webpack.ProvidePlugin({
        FLASK: '@/globals'
      }),
      new webpack.EnvironmentPlugin({
        AIRFLOW_URL: 'http://localhost:5010',
        MELTANO_WEB_APP_URL: 'http://localhost:5000'
      }),
      new HtmlWebpackPlugin({
        filename: 'public/index.html',
        injectFlaskContext: false,
        template: 'public/index.html'
      })
    ]
  },
  devServer: {
    proxy: {
      '^/api': {
        changeOrigin: true,
        target: 'http://localhost:5000',
        ws: true
      }
    }
  }
}
