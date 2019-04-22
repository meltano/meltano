<template>
  <router-view-layout>

    <div slot='left'>
      <ul class="menu-list">
        <router-link
          tag="li"
          :to="{name:'database'}">
          <a>Database</a>
        </router-link>
      </ul>
    </div>

    <div slot="right">
      <router-view />
    </div>

  </router-view-layout>
</template>
<script>
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'Settings',
  components: {
    RouterViewLayout,
  },
  data() {
    return {
      categories: [{
        name: 'Database',
        pages: [{
          title: 'Database',
          href: '/settings/database',
        }],
      }, {
        name: 'Access control',
        pages: [{
          title: 'Roles',
          href: '/settings/roles',
        }],
      }],
    };
  },
};
</script>
