import React from "react";
import { useWindowSize } from "@docusaurus/theme-common";
import BlogSidebarDesktop from "@theme/BlogSidebar/Desktop";
import BlogSidebarMobile from "@theme/BlogSidebar/Mobile";
export default function BlogSidebar({ sidebar, toc }) {
  const windowSize = useWindowSize();
  if (!sidebar?.items.length) {
    return null;
  }
  // Mobile sidebar doesn't need to be server-rendered
  if (windowSize === "mobile") {
    return <BlogSidebarMobile sidebar={sidebar} toc={toc} />;
  }
  return <BlogSidebarDesktop sidebar={sidebar} toc={toc} />;
}
