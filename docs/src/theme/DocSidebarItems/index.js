import React, {memo} from 'react';
import {DocSidebarItemsExpandedStateProvider} from '@docusaurus/theme-common/internal';
import DocSidebarItem from '@theme/DocSidebarItem';
// TODO this item should probably not receive the "activePath" props
// TODO this triggers whole sidebar re-renders on navigation
// eslint-disable-next-line react/prop-types
function DocSidebarItems({items, ...props}) {
  return (
    <DocSidebarItemsExpandedStateProvider>
      {/* eslint-disable-next-line react/prop-types */}
      {items.map((item, index) => (
        <DocSidebarItem key={index} item={item} index={index} {...props} />
      ))}
    </DocSidebarItemsExpandedStateProvider>
  );
}
// Optimize sidebar at each "level"
export default memo(DocSidebarItems);
