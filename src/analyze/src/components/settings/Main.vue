<template>
  <div class="columns">
    <aside class="menu column is-one-quarter section has-background-light">
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
    </aside>
    <div class="column">
      <router-view />
    </div>
  </div>
</template>
<script>
export default {
  name: 'Settings',

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
