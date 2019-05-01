<script>
import { mapActions, mapGetters, mapState } from 'vuex';

import orchestrationsApi from '@/api/orchestrations';

export default {
  name: 'Loaders',
  data() {
    return {
      installingLoaders: [],
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('orchestrations', [
      'getLoaderImageUrl',
      'getLoaderNameWithoutPrefixedTargetDash',
    ]),
    ...mapState('orchestrations', [
      'installedPlugins',
      'loaderInFocus',
      'loaders',
    ]),
    getIsConnectorInstalled() {
      return loader => this.installedPlugins.loaders.find(item => item.name === loader);
    },
    getIsInstallingPlugin() {
      return plugin => this.installingLoaders.includes(plugin);
    },
  },
  methods: {
    ...mapActions('orchestrations', [
      'setLoaderInFocus',
    ]),
    installLoader(loader) {
      this.installingLoaders.push(loader);

      orchestrationsApi.addLoaders({
        name: loader,
      }).then((response) => {
        if (response.status === 200) {
          this.$store.dispatch('orchestrations/getInstalledPlugins')
            .then(() => {
              const idx = this.installingLoaders.indexOf(loader);
              this.installingLoaders.splice(idx, 1);
            });
        }
      });
    },
    updateLoaderSettings(loader) {
      // const loaderObj = this.installedPlugins.loaders.find(item => item.name === loader);
      // this.setLoaderInFocus(loaderObj);
      this.$router.push({ name: 'loaderSettings', params: { loader } });
    },
  },
};
</script>

<template>
  <div>

    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(loader, index) in loaders"
        :key="`${loader}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <img
              :class='{ "grayscale": !getIsConnectorInstalled(loader) }'
              :src='getLoaderImageUrl(loader)'
              :alt="`${getLoaderNameWithoutPrefixedTargetDash(loader)} logo`">
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{loader}}
            </p>

            <template v-if='getIsConnectorInstalled(loader)'>
              <div class="buttons are-small">
                <a
                  class='button is-interactive-primary flex-grow-1'
                  @click="updateLoaderSettings(loader)">Account Settings</a>
                <a class='button' disabled>Uninstall</a>
              </div>
            </template>
            <template v-else>
              <a
                :class='{ "is-loading": getIsInstallingPlugin(loader) }'
                class='button is-interactive-primary is-outlined is-block is-small'
                @click="installLoader(loader)">Install</a>
            </template>

          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
