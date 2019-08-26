module.exports = {
  root: true,
  env: {
    node: true,
    jest: true
  },
  extends: [
    'plugin:vue/essential',
    'plugin:vue/strongly-recommended',
    'plugin:vue/recommended',
    '@vue/prettier'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    // disallow reassignment of function parameters
    // disallow parameter object manipulation except for specific exclusions
    'no-param-reassign': 0,
    curly: ['warn', 'all'],
    'brace-style': ['error', '1tbs'],
    'max-len': ['error', { code: 200, ignoreUrls: true }],
    'no-prototype-builtins': 0
  },
  parserOptions: {
    parser: 'babel-eslint'
  },
  globals: {
    process: false,
    FLASK: false
  }
}
