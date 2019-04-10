<template>
  <router-view-layout>

    <div slot='left'>
      <ul class="menu-list">
        <router-link tag="li" :to="{name:'database', params: {projectSlug: $route.params.projectSlug}}">
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
};
</script>
