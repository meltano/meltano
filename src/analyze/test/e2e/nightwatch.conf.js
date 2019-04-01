require('babel-register');

const config = require('../../config');

// http://nightwatchjs.org/gettingstarted#settings-file
module.exports = {
  src_folders: ['test/e2e/specs'],
  output_folder: 'test/e2e/reports',
  custom_assertions_path: ['test/e2e/custom-assertions'],

  globals: {
    devServerUrl: `http://localhost:${process.env.PORT || config.dev.port}`,
  },

  webdriver: {
    start_process: true,
  },

  test_settings: {
    default: {
      webdriver: {
        server_path: 'node_modules/.bin/chromedriver',
        port: 9515,
        cli_args: [
          '--log', 'debug',
        ],
      },
    },

    chrome: {
      desiredCapabilities: {
        browserName: 'chrome',
        javascriptEnabled: true,
        acceptSslCerts: true,
      },
    },
  },
};
