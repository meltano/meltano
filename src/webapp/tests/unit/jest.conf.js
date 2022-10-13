const path = require('path')

module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/index.js',
    '!**/node_modules/**',
  ],
  coverageDirectory: '<rootDir>/test/unit/coverage',
  mapCoverage: true,
  moduleFileExtensions: ['js', 'json', 'vue'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  rootDir: path.resolve(__dirname, '../../'),
  setupFiles: ['<rootDir>/test/unit/setup'],
  snapshotSerializers: ['<rootDir>/node_modules/jest-serializer-vue'],
  testPathIgnorePatterns: ['<rootDir>/test/e2e'],
  testURL: 'http://localhost:8080',
  transform: {
    '.*\\.(vue)$': '<rootDir>/node_modules/vue-jest',
    '^.+\\.js$': '<rootDir>/node_modules/babel-jest',
  },
}
