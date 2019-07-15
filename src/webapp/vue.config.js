const webpack = require('webpack')

module.exports = {
  devServer: {
    proxy: 'http://localhost:5000'
  },
  configureWebpack: {
    plugins: [
      new webpack.ProvidePlugin({
        FLASK: '@/globals'
      })
    ]
  }
}
