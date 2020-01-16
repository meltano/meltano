<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'
import ConnectorSettingsDropdown from '@/components/pipelines/ConnectorSettingsDropdown'
import utils from '@/utils/utils'

export default {
  name: 'ExtractorSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings,
    ConnectorSettingsDropdown
  },
  data() {
    return {
      isTesting: false,
      localConfiguration: {},
      uploadFormData: null
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'getInstalledPlugin',
      'getIsPluginInstalled',
      'getIsInstallingPlugin'
    ]),
    ...mapGetters('orchestration', ['getHasValidConfigSettings']),
    ...mapState('orchestration', ['extractorInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),

    currentProfile() {
      return this.localConfiguration.profiles[
        this.localConfiguration.profileInFocusIndex
      ]
    },
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
      if (this.isInstalling || this.isLoadingConfigSettings) {
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
    },
    requiredSettingsKeys() {
      return utils.requiredConnectorSettingsKeys(
        this.localConfiguration.settings,
        this.extractor.settingsGroupValidation
      )
    }
  },
  created() {
    this.extractorName = this.$route.params.extractor
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      const needsInstallation = this.extractor.name !== this.extractorName
      const addConfig = {
        pluginType: 'extractors',
        name: this.extractorName
      }

      const uponPlugin = needsInstallation
        ? this.addPlugin(addConfig).then(() => {
            this.getExtractorConfiguration().then(
              this.createEditableConfiguration
            )
            this.installPlugin(addConfig).then(this.tryAutoAdvance)
          })
        : this.getExtractorConfiguration().then(() => {
            this.createEditableConfiguration()
            this.tryAutoAdvance()
          })

      uponPlugin.catch(err => {
        this.$error.handle(err)
        this.close()
      })
    })
  },
  beforeDestroy() {
    this.$store.dispatch('orchestration/resetExtractorInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    ...mapActions('orchestration', [
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
        { profileInFocusIndex: 0 },
        lodash.cloneDeep(this.extractorInFocusConfiguration)
      )
    },
    getExtractorConfiguration() {
      return this.$store.dispatch(
        'orchestration/getExtractorConfiguration',
        this.extractorName
      )
    },
    onChangeUploadFormData(uploadFormData) {
      this.uploadFormData = uploadFormData
    },
    saveConfigAndGoToLoaders() {
      // 1. Prepare conditional upload as response is needed to properly save config settings
      let uponConditionalUpload = this.uploadFormData
        ? this.$store.dispatch('orchestration/uploadPluginConfigurationFile', {
            name: this.extractor.name,
            profileName: this.currentProfile.name,
            type: 'extractors',
            formData: this.uploadFormData
          })
        : Promise.resolve()

      // 2. Initialize conditional request
      uponConditionalUpload.then(response => {
        // 2.a Update setting value with updated and secure file path
        if (response) {
          const payload = response.data
          this.currentProfile.config[payload.settingName] = payload.path
        }

        // 3. Finally save config settings
        this.$store
          .dispatch('orchestration/savePluginConfiguration', {
            name: this.extractor.name,
            type: 'extractors',
            profiles: this.localConfiguration.profiles
          })
          .then(() => {
            this.$store.dispatch('orchestration/updateRecentELTSelections', {
              type: 'extractor',
              value: this.extractor
            })
            this.$router.push({ name: 'loaders' })
            const message = this.extractorLacksConfigSettings
              ? `Auto Advance - No Configuration needed for ${
                  this.extractor.name
                }`
              : `Connection Saved - ${this.extractor.name}`
            Vue.toasted.global.success(message)
          })
          .catch(err => {
            this.$error.handle(err)
            this.close()
          })
      })
    },
    testConnection() {
      this.isTesting = true

      this.testPluginConfiguration({
        name: this.extractor.name,
        type: 'extractors',
        payload: {
          profile: this.currentProfile.name,
          config: this.currentProfile.config
        }
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
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="extractorName" />
        </div>
        <p class="modal-card-title">Extractor Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <div v-if="isLoadingConfigSettings || isInstalling" class="content">
          <div v-if="!isLoadingConfigSettings && isInstalling" class="level">
            <div class="level-item">
              <p class="is-italic">
                Installing {{ extractor.label }} can take up to a minute.
              </p>
            </div>
          </div>
          <progress class="progress is-small is-info"></progress>
        </div>

        <template v-if="!isLoadingConfigSettings">
          <!--
            TEMP ConnectorSettingsDropdown removal from UI.
            Conditional removal so existing users with 2+ profiles already created still can access them
            Get context here https://gitlab.com/meltano/meltano/issues/1389.
          -->
          <template v-if="localConfiguration.profiles.length > 1">
            <ConnectorSettingsDropdown
              v-if="!extractorLacksConfigSettings"
              :connector="extractor"
              plugin-type="extractors"
              :config-settings="localConfiguration"
            ></ConnectorSettingsDropdown>
          </template>

          <ConnectorSettings
            v-if="!extractorLacksConfigSettings"
            field-class="is-small"
            :config-settings="localConfiguration"
            :plugin="extractor"
            :required-settings-keys="requiredSettingsKeys"
            :upload-form-data="uploadFormData"
            :is-show-docs="true"
            @onChangeUploadFormData="onChangeUploadFormData"
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
