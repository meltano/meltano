const webpack = require('webpack')

module.exports = {
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  configureWebpack: {
    plugins: [
      new webpack.ProvidePlugin({
        FLASK: '@/globals'
      }),
      new webpack.EnvironmentPlugin({
        AIRFLOW_URL: 'http://localhost:5010',
        MELTANO_WEB_APP_URL: 'http://localhost:5000'
      })
    ]
  }
}
