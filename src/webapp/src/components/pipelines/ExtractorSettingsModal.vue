<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings
  },
  data() {
    return {
      isTesting: false,
      localConfiguration: {}
    }
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
        this.localConfiguration.settings &&
        this.localConfiguration.settings.length === 0
      )
    },
    extractor() {
      return this.getInstalledPlugin('extractors', this.extractorName)
    },
    isInstalled() {
      return this.getIsPluginInstalled('extractors', this.extractorName)
    },
    isInstalling() {
      return this.getIsInstallingPlugin('extractors', this.extractorName)
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.localConfiguration,
        'config'
      )
    },
    isSaveable() {
      const isValid = this.getHasValidConfigSettings(
        this.localConfiguration,
        this.extractor.settingsGroupValidation
      )
      return !this.isInstalling && this.isInstalled && isValid
    }
  },
  created() {
    this.extractorName = this.$route.params.extractor
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      const needsInstallation = this.extractor.name !== this.extractorName
      if (needsInstallation) {
        const config = {
          pluginType: 'extractors',
          name: this.extractorName
        }
        this.addPlugin(config).then(() => {
          this.getExtractorConfiguration().then(
            this.createEditableConfiguration
          )
          this.installPlugin(config).then(this.tryAutoAdvance)
        })
      } else {
        this.getExtractorConfiguration().then(() => {
          this.createEditableConfiguration()
          this.tryAutoAdvance()
        })
      }
    })
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/resetExtractorInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    ...mapActions('configuration', [
      'savePluginConfiguration',
      'testPluginConfiguration',
      'updateRecentELTSelections'
    ]),
    tryAutoAdvance() {
      if (this.extractorLacksConfigSettings) {
        this.saveConfigAndGoToLoaders()
      }
    },
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'extractors' })
      }
    },
    createEditableConfiguration() {
      this.localConfiguration = Object.assign(
        {},
        lodash.cloneDeep(this.extractorInFocusConfiguration)
      )
    },
    getExtractorConfiguration() {
      return this.$store.dispatch(
        'configuration/getExtractorConfiguration',
        this.extractorName
      )
    },
    saveConfigAndGoToLoaders() {
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          name: this.extractor.name,
          type: 'extractors',
          config: this.localConfiguration.config
        })
        .then(() => {
          this.$store.dispatch('configuration/updateRecentELTSelections', {
            type: 'extractor',
            value: this.extractor
          })
          this.$router.push({ name: 'loaders' })
          const message = this.extractorLacksConfigSettings
            ? `Auto Advance - No Configuration needed for ${this.extractor.name}`
            : `Connection Saved - ${this.extractor.name}`
          Vue.toasted.global.success(message)
        })
      const message = this.extractorLacksConfigSettings
        ? `Auto Advance - No Configuration needed for ${this.extractor.name}`
        : `Connection Saved - ${this.extractor.name}`
      Vue.toasted.global.success(message)
    },
    testConnection() {
      this.isTesting = true
      this.testPluginConfiguration({
        name: this.extractor.name,
        type: 'extractors',
        config: this.localConfiguration.config
      })
        .then(response => {
          if (response.data.isSuccess) {
            Vue.toasted.global.success(
              `Valid Extractor Connection - ${this.extractor.name}`
            )
          } else {
            Vue.toasted.global.error(
              `Invalid Extractor Connection - ${this.extractor.name}`
            )
          }
        })
        .finally(() => (this.isTesting = false))
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-narrow">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="extractorName" />
        </div>
        <p class="modal-card-title">Extractor Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div v-if="isLoadingConfigSettings || isInstalling" class="content">
          <div v-if="!isLoadingConfigSettings && isInstalling" class="level">
            <div class="level-item">
              <p class="is-italic">
                Installing {{ extractorName }} can take up to a minute.
              </p>
            </div>
          </div>
          <progress class="progress is-small is-info"></progress>
        </div>

        <template v-if="!isLoadingConfigSettings">
          <ConnectorSettings
            v-if="!extractorLacksConfigSettings"
            field-class="is-small"
            :config-settings="localConfiguration"
            :plugin="extractor"
          />
        </template>
      </section>
      <footer class="modal-card-foot field is-grouped is-grouped-right">
        <button class="button" @click="close">Cancel</button>
        <div class="field has-addons">
          <div class="control">
            <button
              class="button"
              :class="{ 'is-loading': isTesting }"
              :disabled="!isSaveable"
              @click="testConnection"
            >
              Test Connection
            </button>
          </div>
          <div class="control">
            <button
              class="button is-interactive-primary"
              :disabled="!isSaveable || isTesting"
              @click="saveConfigAndGoToLoaders"
            >
              Save
            </button>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
