import React from 'react';
import { ThemeClassNames } from '@docusaurus/theme-common';
import { useDoc } from '@docusaurus/theme-common/internal';
import TOC from '@theme/TOC';
export default function DocItemTOCDesktop() {
  const { toc, frontMatter } = useDoc();
  return (
    <TOC
      toc={toc}
      type="docs"
      minHeadingLevel={frontMatter.toc_min_heading_level}
      maxHeadingLevel={frontMatter.toc_max_heading_level}
      className={ThemeClassNames.docs.docTocDesktop}
    />
  );
}
