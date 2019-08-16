<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'Loaders',
  components: {
    ConnectorLogo
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin']),
    ...mapState('plugins', ['plugins'])
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    installLoaderAndBeginSettings(loader) {
      this.addPlugin({ pluginType: 'loaders', name: loader }).then(() => {
        this.installPlugin({ pluginType: 'loaders', name: loader })
        this.updateLoaderSettings(loader)
      })
    },
    updateLoaderSettings(loader) {
      this.$router.push({ name: 'loaderSettings', params: { loader } })
    }
  }
}
</script>

<template>
  <div>
    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class="content has-text-centered">
          <p class="level-item buttons">
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Tell us which loader(s) to install</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Configure and save their settings</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <div class="tile is-ancestor is-flex is-flex-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(loader, index) in plugins.loaders"
        :key="`${loader}-${index}`"
      >
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo
              :connector="loader"
              :is-grayscale="!getIsPluginInstalled('loaders', loader)"
            />
          </div>
          <div class="content is-small">
            <p class="has-text-centered">
              {{ loader }}
            </p>

            <template v-if="getIsPluginInstalled('loaders', loader)">
              <div class="buttons are-small">
                <a
                  class="button is-interactive-primary flex-grow-1"
                  @click="updateLoaderSettings(loader)"
                  >Configure</a
                >
                <a
                  class="button tooltip is-tooltip-warning is-tooltip-multiline"
                  data-tooltip="This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues."
                  >Uninstall</a
                >
              </div>
            </template>
            <template v-else>
              <a
                :class="{
                  'is-loading': getIsInstallingPlugin('loaders', loader)
                }"
                class="button is-interactive-primary is-outlined is-block is-small"
                @click="installLoaderAndBeginSettings(loader)"
                >Install</a
              >
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
