const ctx = require.context(
  '@site/docs/reference/cloud/api/resources',
  true,
  /^\.\/_snippets\/.*\.md$/,
);

console.debug(ctx.keys());

const Snippet = ({ path }) => {
  const key = `./_snippets/${path}`;

  if (!ctx.keys().includes(key)) {
    console.warn(`Snippet not found: ${key}`);
    return null;
  }

  const { default: Component } = ctx(key);
  return <Component />;
};

export default Snippet;
