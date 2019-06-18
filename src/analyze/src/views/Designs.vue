<script>
import RouterViewLayout from '@/views/RouterViewLayout';
import DocsLink from '@/components/generic/DocsLink';

export default {
  name: 'Designs',
  components: {
    RouterViewLayout,
    DocsLink,
  },
  methods: {
    isCurrentLink(path) {
      return this.$route.path === path ? 'is-active' : '';
    },
  },
};
</script>

<template>
  <router-view-layout>

    <div class="container view-header">
      <div class="content">
        <div class="level">
          <div class="level-left">
            <h1 class='is-marginless'>Analyze</h1>
          </div>
          <div class="level-right">
            <div class="tabs is-right">
              <ul>
                <li :class="isCurrentLink('/analyze/models/')">
                  <router-link to="/analyze/models/">Models</router-link>
                </li>
                <li :class="isCurrentLink('/analyze/connection-settings/')" class="is-marginless">
                  <router-link to="/analyze/connection-settings/">Connections</router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container view-body">
      <router-view />
    </div>

  </router-view-layout>
</template>

<style lang="scss">
</style>
