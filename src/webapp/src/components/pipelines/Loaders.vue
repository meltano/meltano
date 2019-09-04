<script>
import { mapGetters, mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import SpeedRunIcon from '@/components/pipelines/SpeedRunIcon'

export default {
  name: 'Loaders',
  components: {
    ConnectorLogo,
    SpeedRunIcon
  },
  data: () => ({
    speedRunLoader: 'target-sqlite'
  }),
  computed: {
    ...mapGetters('plugins', [
      'getIsAddingPlugin',
      'getIsInstallingPlugin',
      'getIsPluginInstalled'
    ]),
    ...mapState('plugins', ['plugins']),
    sortedLoaders() {
      // This is a stop gap until we implement an eventual need for automatic text filtering for cards
      const currentLoaders = this.plugins.loaders || []
      let newLoaders = []

      if (currentLoaders.length > 0) {
        newLoaders = [this.speedRunLoader].concat(
          currentLoaders.filter(plugin => plugin !== this.speedRunLoader)
        )
      }

      return newLoaders
    }
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  methods: {
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
        v-for="(loader, index) in sortedLoaders"
        :key="`${loader}-${index}`"
        class="tile is-parent is-3 is-relative"
      >
        <div class="tile level is-child box">
          <SpeedRunIcon v-if="loader === speedRunLoader" />
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
                  class="button tooltip is-tooltip-warning"
                  data-tooltip="Help shape this feature by contributing your ideas"
                  target="_blank"
                  href="https://gitlab.com/meltano/meltano/issues?scope=all&utf8=%E2%9C%93&state=opened&search=uninstall"
                  >Uninstall</a
                >
              </div>
            </template>
            <template v-else>
              <a
                :class="{
                  'is-loading':
                    getIsAddingPlugin('loaders', loader) ||
                    getIsInstallingPlugin('loaders', loader)
                }"
                class="button is-interactive-primary is-outlined is-block is-small"
                @click="updateLoaderSettings(loader)"
                >Install</a
              >
            </template>
          </div>
        </div>
      </div>
    </div>
    <progress
      v-if="!plugins.loaders"
      class="progress is-small is-info"
    ></progress>
  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
