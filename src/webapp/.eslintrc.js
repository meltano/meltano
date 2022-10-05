module.exports = {
  env: {
    jest: true,
    node: true,
  },
  extends: [
    'plugin:vue/essential',
    'plugin:vue/strongly-recommended',
    'plugin:vue/recommended',
    '@vue/prettier',
    'prettier',
  ],
  globals: {
    FLASK: false,
    process: false,
    cy: false,
  },
  parserOptions: {
    parser: '@babel/eslint-parser',
  },
  plugins: ['prettier'],
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
        ignoreUrls: true,
      },
    ],
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': 'error',
    // disallow reassignment of function parameters
    // disallow parameter object manipulation except for specific exclusions
    'no-param-reassign': 0,
    'no-prototype-builtins': 0,
    'sort-vars': 2,
    'prettier/prettier': ['error', { singleQuote: true }],
    quotes: [
      'error',
      'single',
      { avoidEscape: true, allowTemplateLiterals: true },
    ],
    'vue/multi-word-component-names': [
      'error',
      {
        ignores: [
          'Dropdown',
          'Embed',
          'Logo',
          'Message',
          'Pill',
          'Pipeline',
          'Pipelines',
          'Plugin',
          'Plugins',
          'Roles',
          'Settings',
          'Step',
        ],
      },
    ],
  },
}
