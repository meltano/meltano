<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings
  },
  computed: {
    ...mapGetters('plugins', [
      'getInstalledPlugin',
      'getIsPluginInstalled',
      'getIsInstallingPlugin'
    ]),
    ...mapGetters('configuration', ['getHasValidConfigSettings']),
    ...mapState('configuration', ['extractorInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),
    extractorLacksConfigSettings() {
      return (
        this.extractorInFocusConfiguration.settings &&
        this.extractorInFocusConfiguration.settings.length === 0
      )
    },
    extractor() {
      return this.getInstalledPlugin('extractors', this.extractorNameFromRoute)
    },
    isInstalled() {
      return this.getIsPluginInstalled(
        'extractors',
        this.extractorNameFromRoute
      )
    },
    isInstalling() {
      return this.getIsInstallingPlugin(
        'extractors',
        this.extractorNameFromRoute
      )
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.extractorInFocusConfiguration,
        'config'
      )
    },
    isSaveable() {
      const isValid = this.getHasValidConfigSettings(
        this.extractorInFocusConfiguration,
        this.extractor.settingsGroupValidation
      )
      return !this.isInstalling && this.isInstalled && isValid
    }
  },
  created() {
    this.extractorNameFromRoute = this.$route.params.extractor
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      const needsInstallation =
        this.extractor.name !== this.extractorNameFromRoute
      if (needsInstallation) {
        const config = {
          pluginType: 'extractors',
          name: this.extractorNameFromRoute
        }
        this.addPlugin(config).then(() => {
          this.prepareExtractorConfiguration()
          this.installPlugin(config)
        })
      } else {
        this.prepareExtractorConfiguration()
      }
    })
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/resetExtractorInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'extractors' })
      }
    },
    prepareExtractorConfiguration() {
      this.$store
        .dispatch(
          'configuration/getExtractorConfiguration',
          this.extractorNameFromRoute
        )
        .then(() => {
          if (this.extractorLacksConfigSettings) {
            this.saveConfigAndBeginEntitySelection()
          }
        })
    },
    saveConfigAndBeginEntitySelection() {
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          name: this.extractor.name,
          type: 'extractors',
          config: this.extractorInFocusConfiguration.config
        })
        .then(() => {
          this.$store.dispatch('configuration/updateRecentELTSelections', {
            type: 'extractor',
            value: this.extractor
          })
          this.$router.push({
            name: 'extractorEntities',
            params: { extractor: this.extractor.name }
          })
          Vue.toasted.global.success(
            `Connection Saved - ${this.extractor.name}`
          )
        })
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-narrow">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="extractorNameFromRoute" />
        </div>
        <p class="modal-card-title">Extractor Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div v-if="isLoadingConfigSettings || isInstalling" class="content">
          <div v-if="!isLoadingConfigSettings && isInstalling" class="level">
            <div class="level-item">
              <p class="is-italic">
                Installing {{ extractorNameFromRoute }} can take up to a minute.
              </p>
            </div>
          </div>
          <progress class="progress is-small is-info"></progress>
        </div>

        <template v-if="!isLoadingConfigSettings">
          <ConnectorSettings
            v-if="!extractorLacksConfigSettings"
            field-class="is-small"
            :config-settings="extractorInFocusConfiguration"
          />
          <div v-if="extractor.docs" class="content has-text-centered mt1r">
            <p>
              View Meltano's
              <a
                :href="extractor.docs"
                target="_blank"
                class="has-text-underlined"
                >{{ extractorNameFromRoute }} docs</a
              >
              for more info.
            </p>
          </div>
        </template>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!isSaveable"
          @click="saveConfigAndBeginEntitySelection"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
