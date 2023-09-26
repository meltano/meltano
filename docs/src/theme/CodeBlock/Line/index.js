import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
export default function CodeBlockLine({
  // eslint-disable-next-line react/prop-types
  line,
  // eslint-disable-next-line react/prop-types
  classNames,
  // eslint-disable-next-line react/prop-types
  showLineNumbers,
  // eslint-disable-next-line react/prop-types
  getLineProps,
  // eslint-disable-next-line react/prop-types
  getTokenProps,
}) {
  // eslint-disable-next-line react/prop-types
  if (line.length === 1 && line[0].content === '\n') {
    // eslint-disable-next-line react/prop-types
    line[0].content = '';
  }

  // eslint-disable-next-line react/prop-types
  const lineIsHighlight = line.some((l) => l.content.includes('=='));

  // eslint-disable-next-line react/prop-types
  line.map((l) => {
    l.content.includes('==')
      ? (l.content = l.content.replace('==', ''))
      : l.content;
    return l;
  });

  const lineProps = getLineProps({
    line,
    className: clsx(
      classNames,
      showLineNumbers && styles.codeLine,
      lineIsHighlight && styles.highlightedLine
    ),
  });
  // eslint-disable-next-line react/prop-types
  const lineTokens = line.map((token, key) => (
    <span key={key} {...getTokenProps({ token, key })} />
  ));
  return (
    <span {...lineProps}>
      {showLineNumbers ? (
        <>
          <span className={styles.codeLineNumber} />
          <span className={styles.codeLineContent}>{lineTokens}</span>
        </>
      ) : (
        lineTokens
      )}
      <br />
    </span>
  );
}
