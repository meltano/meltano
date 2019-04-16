<template>
  <router-view-layout-sidebar>

    <div slot='left'>
      <ul class="menu-list">
        <router-link
          tag="li"
          :to="{name:'database', params: {projectSlug: currentProjectSlug}}">
          <a>Database</a>
        </router-link>
        <router-link
          tag="li"
          :to="{name:'connectors', params: {projectSlug: currentProjectSlug}}">
          <a>Connectors</a>
        </router-link>
      </ul>
    </div>

    <div slot="right">
      <router-view />
    </div>

  </router-view-layout-sidebar>
</template>
<script>
import { mapState } from 'vuex';

import RouterViewLayoutSidebar from '@/views/RouterViewLayoutSidebar';

export default {
  name: 'Settings',
  components: {
    RouterViewLayoutSidebar,
  },
  computed: {
    ...mapState('projects', [
      'currentProjectSlug',
    ]),
  },
  data() {
    return {
      categories: [
        {
          name: 'Database',
          pages: [{
            title: 'Database',
            href: '/settings/database',
          }],
        },
        {
          name: 'Access control',
          pages: [{
            title: 'Roles',
            href: '/settings/roles',
          }],
        },
        {
          name: 'Connectors',
          pages: [
            {
              title: 'Extractors',
              href: '/settings/connectors#extractors',
            },
            {
              title: 'Loaders',
              href: '/settings/connectors#loaders',
            },
          ],
        },
      ],
    };
  },
};
</script>
