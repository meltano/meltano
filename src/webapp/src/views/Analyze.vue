<script>
import RouterViewLayout from '@/views/RouterViewLayout';
import DocsLink from '@/components/generic/DocsLink';

export default {
  name: 'Analyze',
  components: {
    RouterViewLayout,
    DocsLink,
  },
  computed: {
    isAnalyzing() {
      return !this.isCurrentLink('/analyze/models/') &&
        !this.isCurrentLink('/analyze/settings/');
    },
    isCurrentLink() {
      return path => this.$route.path === path;
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
                <li :class="{ 'is-active': isCurrentLink('/analyze/models/') }">
                  <router-link :to="{name: 'analyzeModels'}">Models</router-link>
                </li>
                <li
                  class="is-marginless"
                  :class="{ 'is-active': isCurrentLink('/analyze/settings/') }">
                  <router-link :to="{name: 'analyzeSettings'}">Connections</router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      class="container view-body"
      :class="{ 'is-fluid': isAnalyzing }">
      <router-view />
    </div>

  </router-view-layout>
</template>

<style lang="scss">
</style>
