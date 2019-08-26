module.exports = {
  env: {
    jest: true,
    node: true
  },
  extends: [
    'plugin:vue/essential',
    'plugin:vue/strongly-recommended',
    'plugin:vue/recommended',
    '@vue/prettier'
  ],
  globals: {
    FLASK: false,
    process: false
  },
  parserOptions: {
    parser: 'babel-eslint'
  },
  root: true,
  rules: {
    'brace-style': ['error', '1tbs'],
    curly: ['warn', 'all'],
    'max-len': ['error', { code: 200, ignoreUrls: true }],
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    // disallow reassignment of function parameters
    // disallow parameter object manipulation except for specific exclusions
    'no-param-reassign': 0,
    'no-prototype-builtins': 0,
    'sort-vars': 2
  }
}
