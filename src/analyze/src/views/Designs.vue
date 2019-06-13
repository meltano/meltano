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
    <div class="container">
      <div class="content">
        <!-- <ClosableMessage title="Meltano Analyze">
          <p>
            <span class="has-text-weight-bold">Meltano</span> streamlines the collection, analysis, and dashboarding of data.
          </p>
          <p>
            <span class="is-italic">You need to connect to pipelined data first</span>. Manage your connections below to enable analyses.
          </p>
        </ClosableMessage> -->
        <div class="level">
          <div class="level-left">
            <h1>Analyze</h1>
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

      <router-view />

    </div>
  </router-view-layout>
</template>

<style lang="scss">
.level .tabs ul,
.level .tabs a {
  border-bottom-color: white;
}

.level .tabs li.is-active a {
    border-bottom-color: #1f78d1;
    color: #1f78d1;
}

.level .tabs a:hover {
  color: #363636;
  border-bottom-color: #363636;
}
</style>
