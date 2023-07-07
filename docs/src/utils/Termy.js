import React, { useEffect, useRef } from "react";
import { Termynal } from "./Termynal";
import { MDXProvider } from "@mdx-js/react";

function Termy({ children, options }) {
  const containerRef = useRef(null);
  const termynalRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && children) {
      const lines = React.Children.map(children, (child) => {
        const lineData = {
          value: child.props.children,
          ...child.props.lineData,
        };
        return lineData;
      });

      termynalRef.current = new Termynal(containerRef.current, {
        lineData: lines,
        ...options,
      });
    }

    return () => {
      if (termynalRef.current) {
        termynalRef.current.container.innerHTML = "";
      }
    };
  }, [children, options]);

  return (
    <MDXProvider>
      <div ref={containerRef}>{children}</div>
    </MDXProvider>
  );
}

export default Termy;
