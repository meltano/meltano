<script>
import RouterViewLayout from '@/views/RouterViewLayout';
import ClosableMessage from '@/components/generic/ClosableMessage';

export default {
  name: 'Designs',
  components: {
    RouterViewLayout,
    ClosableMessage,
  },
  methods: {
    isCurrentLink(path) {
      if (this.$route.path === path) {
        return 'is-active';
      }
      return '';
    },
  },
};
</script>

<template>
  <router-view-layout>
    <div class="container">
      <div class="content">
        <ClosableMessage title="Meltano Analyze">
          <p>
            <span class="has-text-weight-bold">Meltano</span> streamlines the collection, analysis, and dashboarding of data.
          </p>
          <p>
            <span class="is-italic">You need to connect to pipelined data first</span>. Manage your connections below to enable analyses.
          </p>
        </ClosableMessage>
        <div class="level">
          <div class="level-left">
            <h1>Analyze</h1>
          </div>
          <div class="level-right">
            <div class="tabs is-right">
              <ul>
                <li :class="isCurrentLink('/analyze/models')">
                  <router-link to="/analyze/models">Models</router-link>
                </li>
                <li :class="isCurrentLink('/analyze/settings')" class="is-marginless">
                  <router-link to="/analyze/settings">Settings</router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <router-view />
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
</style>
