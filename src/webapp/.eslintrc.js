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
    process: false,
    cy: false
  },
  parserOptions: {
    parser: 'babel-eslint'
  },
  root: true,
  rules: {
    'brace-style': ['error', '1tbs'],
    curly: ['warn', 'all'],
    'max-len': [
      'error',
      {
        code: 200,
        ignorePattern: ' d=".+"', // Ignore path commands of an SVG element
        ignoreTemplateLiterals: true,
        ignoreUrls: true
      }
    ],
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': 'error',
    // disallow reassignment of function parameters
    // disallow parameter object manipulation except for specific exclusions
    'no-param-reassign': 0,
    'no-prototype-builtins': 0,
    'sort-vars': 2
  }
}
