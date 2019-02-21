<template>
  <router-view-layout>

    <div slot='left'>
      <template v-for="category in categories">
        <div :key="category.name">
          <p class="menu-label">
            {{category.name}}
          </p>
          <ul class="menu-list">
            <router-link tag="li" :key="page.href" :to="page.href" v-for="page in category.pages">
              <a>{{page.title}}</a>
            </router-link>
          </ul>
        </div>
      </template>
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
