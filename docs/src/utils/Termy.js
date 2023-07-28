import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Termynal } from './Termynal';
import { MDXProvider } from '@mdx-js/react';

const progressLiteralStart = '---> 100%';
const promptLiteralStart = '$ ';
const customPromptLiteralStart = '# ';
// eslint-disable-next-line no-unused-vars
const codeThingy = '```';
const waitStart = '<---';

// eslint-disable-next-line react/prop-types
function Termy({ children, options }) {
  const containerRef = useRef(null);
  const termynalRef = useRef(null);

  const [isIntersecting, setIntersecting] = useState(false);
  const [observerTriggered, setObserverTriggered] = useState(false);

  const observer = useMemo(() => {
    if (typeof window === 'undefined' || !window.IntersectionObserver) return;
    return new IntersectionObserver(([entry]) => {
      if (!observerTriggered && entry.isIntersecting) {
        setIntersecting(true);
        setObserverTriggered(true);
      }
    });
  }, [containerRef]);

  useEffect(() => {
    if (containerRef.current && children) {
      observer.observe(containerRef.current);

      // eslint-disable-next-line react/prop-types
      const lines = children.props.children.props?.children.split('\n');

      const lineArray = lines.map((line) => {
        return { value: line, class: 'block' };
      });

      for (let string of lineArray) {
        if (string.value === '') {
          string.value = '<br />';
        } else if (string.value === progressLiteralStart) {
          string.type = 'progress';
        } else if (string.value.startsWith(promptLiteralStart)) {
          const value = string.value.replace(promptLiteralStart, '').trimEnd();
          string.type = 'input';
          string.value = value;
        } else if (string.value.startsWith('// ')) {
          const value = '💬 ' + string.value.replace('// ', '').trimEnd();
          string.value = value;
          string.class = 'termynal-comment';
          string.delay = 0;
        } else if (string.value == waitStart) {
          string.type = 'wait';
          string.delay = 1;
          string.value = '<br />';
        } else if (string.value.startsWith(customPromptLiteralStart)) {
          const promptStart = string.indexOf(promptLiteralStart);
          if (promptStart === -1) {
            console.error(
              'Custom prompt found but no end delimiter',
              string.value
            );
          }
          const prompt = string.value
            .slice(0, promptStart)
            .replace(customPromptLiteralStart, '');
          let value = string.value.slice(
            promptStart + promptLiteralStart.length
          );
          string.type = 'input';
          string.value = value;
          string.prompt = prompt;
        } else {
          string.delay = 0;
        }
      }

      lineArray.join('<br/>');

      termynalRef.current = new Termynal(containerRef.current, {
        lineData: lineArray,
        noInit: !isIntersecting,
        lineDelay: 500,
      });
    }

    return () => {
      if (termynalRef.current) {
        termynalRef.current.container.innerHTML = '';
      }
      observer.disconnect();
    };
  }, [children, options, isIntersecting]);

  return (
    <MDXProvider>
      <div ref={containerRef}>{children}</div>
    </MDXProvider>
  );
}

export default Termy;
