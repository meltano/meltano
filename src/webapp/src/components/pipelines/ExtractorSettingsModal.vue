<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'
import ConnectorSettingsDropdown from '@/components/pipelines/ConnectorSettingsDropdown'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings,
    ConnectorSettingsDropdown
  },
  data() {
    return {
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
        'profiles'
      )
    },
    isSaveable() {
      if (this.isLoadingConfigSettings) {
        return
      }
      const configSettings = {
        config: this.localConfiguration.profiles[
          this.localConfiguration.profileInFocusIndex
        ].config,
        settings: this.localConfiguration.settings
      }
      const isValid = this.getHasValidConfigSettings(
        configSettings,
        this.extractor.settingsGroupValidation
      )
      return this.isInstalled && isValid
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
        { profileInFocusIndex: 0 },
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
          profiles: this.localConfiguration.profiles
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
          <ConnectorSettingsDropdown
            v-if="!extractorLacksConfigSettings"
            :connector="extractor"
            plugin-type="extractors"
            :config-settings="localConfiguration"
          ></ConnectorSettingsDropdown>

          <ConnectorSettings
            v-if="!extractorLacksConfigSettings"
            field-class="is-small"
            :config-settings="localConfiguration"
          />
          <div v-if="extractor.docs" class="content has-text-centered mt1r">
            <p>
              View Meltano's
              <a
                :href="extractor.docs"
                target="_blank"
                class="has-text-underlined"
                >{{ extractorName }} docs</a
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
          @click="saveConfigAndGoToLoaders"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
