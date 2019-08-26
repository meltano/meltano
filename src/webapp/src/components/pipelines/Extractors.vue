<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'Extractors',
  components: {
    ConnectorLogo
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin']),
    ...mapState('plugins', ['plugins']),
    isLoadingExtractors() {
      return this.plugins.extractors && this.plugins.extractors.length === 0
    }
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    installExtractorAndBeginSettings(extractor) {
      this.addPlugin({ pluginType: 'extractors', name: extractor }).then(() => {
        this.installPlugin({ pluginType: 'extractors', name: extractor })
        this.updateExtractorSettings(extractor)
      })
    },
    updateExtractorSettings(extractor) {
      this.$router.push({ name: 'extractorSettings', params: { extractor } })
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
              <span>Tell us which extractor(s) to install</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Configure and save their settings</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <progress
      v-if="isLoadingExtractors"
      class="progress is-small is-info"
    ></progress>

    <div v-else class="tile is-ancestor is-flex is-flex-wrap">
      <div
        v-for="(extractor, index) in plugins.extractors"
        :key="`${extractor}-${index}`"
        class="tile is-parent is-3"
      >
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo
              :connector="extractor"
              :is-grayscale="!getIsPluginInstalled('extractors', extractor)"
            />
          </div>
          <div class="content is-small">
            <p class="has-text-centered">
              {{ extractor }}
            </p>

            <template v-if="getIsPluginInstalled('extractors', extractor)">
              <div class="buttons are-small">
                <a
                  class="button is-interactive-primary flex-grow-1"
                  @click="updateExtractorSettings(extractor)"
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
                  'is-loading': getIsInstallingPlugin('extractors', extractor)
                }"
                class="button is-interactive-primary is-outlined is-block is-small"
                @click="installExtractorAndBeginSettings(extractor)"
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
