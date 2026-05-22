import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';
import Snippet from './Snippet';
import ctx from './snippetContext';

const TABS = [
  { value: 'curl', label: 'cURL', file: 'curl-request.md' },
  { value: 'python', label: 'Python (requests)', file: 'python-requests.md' },
];

const Examples = ({ path }) => {
  const available = TABS.filter(({ file }) =>
    ctx.keys().includes(`./_snippets/${path}/${file}`)
  );

  if (available.length === 0) return null;

  return <>
    <h5>Examples</h5>
    <Tabs className="meltano-tabs">
      {available.map(({ value, label, file }) => (
        <TabItem
          key={value}
          className="meltano-tab-content"
          value={value}
          label={label}
        >
          <Snippet path={`${path}/${file}`} />
        </TabItem>
      ))}
    </Tabs>
  </>;
};

export default Examples;
