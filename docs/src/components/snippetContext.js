const ctx = require.context(
  '@site/docs/reference/cloud/api/resources',
  true,
  /^\.\/_snippets\/.*\.md$/,
);

console.debug(ctx.keys());

export default ctx;
