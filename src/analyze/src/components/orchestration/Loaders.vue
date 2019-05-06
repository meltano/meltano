<script>
import { mapState } from 'vuex';

import Database from '@/components/orchestration/Database';

import orchestrationsApi from '@/api/orchestrations';

export default {
  name: 'Loaders',
  components: {
    Database,
  },
  data() {
    return {
      filterLoadersText: '',
      installingLoaders: [],
      loaderInFocus: null,
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
  },
  computed: {
    ...mapState('orchestrations', [
      'installedPlugins',
      'loaders',
    ]),
    getImageUrl() {
      return loader => `/static/logos/${this.getNameWithoutPrefixedTapDash(loader)}-logo.png`;
    },
    getIsConnectorInstalled() {
      return loader => this.installedPlugins.loaders.find(item => item.name === loader);
    },
    getIsInstallingPlugin() {
      return plugin => this.installingLoaders.includes(plugin);
    },
    getNameWithoutPrefixedTapDash() {
      return loader => loader.replace('target-', '');
    },
    filteredLoaders() {
      if (this.filterLoadersText) {
        return this.loaders
          .filter(item => item.indexOf(this.filterLoadersText) > -1);
      }
      return this.loaders;
    },
  },
  methods: {
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
    updateLoaderInFocus(loader) {
      const loaderObj = this.installedPlugins.loaders.find(item => item.name === loader);
      this.loaderInFocus = loaderObj;
    },
  },
};
</script>

<template>
  <div>
    <div v-if='loaderInFocus'>

      <Database
        @clearLoaderInFocus='updateLoaderInFocus(null)'>
      </Database>

    </div>

    <div v-else>
      <div
        v-if="filteredLoaders.length === 0"
        class='content'>
        <p>
          No loaders are available.
        </p>
      </div>

      <template v-else>
        <div class="columns">
          <div class="column is-4 is-offset-4">
            <input
              type="text"
              v-model="filterLoadersText"
              placeholder="Filter loaders..."
              class="input connector-input">
          </div>
        </div>

        <div class="tile is-ancestor flex-and-wrap">
          <div
            class="tile is-parent is-3"
            v-for="(loader, index) in filteredLoaders"
            :key="`${loader}-${index}`">
            <div class="tile level is-child box">
              <div class="image level-item is-64x64 container">
                <img
                  :class='{ "grayscale": !getIsConnectorInstalled(loader) }'
                  :src='getImageUrl(loader)'
                  :alt="`${getNameWithoutPrefixedTapDash(loader)} logo`">
              </div>
              <div class="content is-small">
                <p class='has-text-centered'>
                  {{loader}}
                </p>

                <template v-if='getIsConnectorInstalled(loader)'>
                  <div class="buttons are-small">
                    <a
                      class='button is-success flex-grow-1'
                      @click="updateLoaderInFocus(loader)">Account Settings</a>
                    <a
                      class='button tooltip is-tooltip-warning is-tooltip-multiline'
                      data-tooltip='This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues.'>Uninstall</a>
                  </div>
                </template>
                <template v-else>
                  <a
                    :class='{ "is-loading": getIsInstallingPlugin(loader) }'
                    class='button is-success is-outlined is-block is-small'
                    @click="installLoader(loader)">Install</a>
                </template>

              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
