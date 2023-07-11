import React from "react";
import clsx from "clsx";
import styles from "./styles.module.css";
export default function CodeBlockLine({
  line,
  classNames,
  showLineNumbers,
  getLineProps,
  getTokenProps,
}) {
  if (line.length === 1 && line[0].content === "\n") {
    line[0].content = "";
  }

  const lineIsHighlight = line.some((l) => l.content.includes("=="));
  line.map((l) => {
    l.content.includes("==")
      ? (l.content = l.content.replace("==", ""))
      : l.content;
    console.log(l.content);
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
