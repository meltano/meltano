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
      isSaving: false,
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
    ...mapGetters('orchestration', [
      'getHasPipelineWithExtractor',
      'getHasValidConfigSettings',
      'getPipelineWithExtractor'
    ]),
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
    },
    submittedProfiles() {
      if (this.extractor.name === 'tap-gitlab') {
        return this.localConfiguration.profiles.map(profile => {
          if (profile.config.hasOwnProperty('source')) {
            delete profile.config.source
          }

          return profile
        })
      } else {
        return this.localConfiguration.profiles
      }
    }
  },
  created() {
    this.extractorName = this.$route.params.extractor
    const needsInstallation = this.extractor.name !== this.extractorName
    const addConfig = {
      pluginType: 'extractors',
      name: this.extractorName
    }

    const uponPlugin = needsInstallation
      ? this.addPlugin(addConfig).then(() => {
          this.$store.dispatch('plugins/getInstalledPlugins')
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
  },
  beforeDestroy() {
    this.$store.dispatch('orchestration/resetExtractorInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    ...mapActions('orchestration', [
      'savePluginConfiguration',
      'testPluginConfiguration'
    ]),
    tryAutoAdvance() {
      if (this.extractorLacksConfigSettings) {
        this.save()
      }
    },
    close() {
      this.$router.push({ name: 'extractors' })
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
    save() {
      this.isSaving = true

      // 1. Prepare conditional upload as response is needed to properly save config settings
      let uponConditionalUpload = this.uploadFormData
        ? this.$store.dispatch('orchestration/uploadPluginConfigurationFile', {
            name: this.extractor.name,
            profileName: this.currentProfile.name,
            type: 'extractors',
            payload: this.uploadFormData
          })
        : Promise.resolve()

      // 2. Initialize conditional request
      uponConditionalUpload.then(response => {
        // 2.a Update setting value with updated and secure file path
        if (response) {
          const payload = response.data
          this.currentProfile.config[payload.settingName] = payload.path
        }

        // 3. Save config settings
        this.savePluginConfiguration({
          name: this.extractor.name,
          type: 'extractors',
          profiles: this.submittedProfiles
        })
          .then(() => {
            const message = this.extractorLacksConfigSettings
              ? `No configuration needed for ${this.extractor.name}`
              : `Configuration saved - ${this.extractor.name}`
            Vue.toasted.global.success(message)
            this.close()
          })
          .catch(error => {
            this.$error.handle(error)
          })
          .finally(() => (this.isSaving = false))
      })
    },
    testConnection() {
      this.isTesting = true

      // 1. Prepare conditional upload as response is needed to properly save config settings
      let uponConditionalUpload = this.uploadFormData
        ? this.$store.dispatch('orchestration/uploadPluginConfigurationFile', {
            name: this.extractor.name,
            profileName: this.currentProfile.name,
            type: 'extractors',
            payload: { ...this.uploadFormData, tmp: true }
          })
        : Promise.resolve()

      // 2. Initialize conditional request
      uponConditionalUpload.then(response => {
        // 2.a Update setting value with updated and secure file path
        if (response) {
          const payload = response.data
          this.currentProfile.config[payload.settingName] = payload.path
        }

        // 3. Save config settings
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
          .then(() => {
            if (this.uploadFormData) {
              return this.$store.dispatch(
                'orchestration/deleteUploadedPluginConfigurationFile',
                {
                  name: this.extractor.name,
                  profileName: this.currentProfile.name,
                  type: 'extractors',
                  payload: {
                    ...this.uploadFormData,
                    file: null,
                    tmp: true
                  }
                }
              )
            }
          })
          .finally(() => (this.isTesting = false))
      })
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div :class="{ 'modal-card': true, 'is-wide': !!extractor.docs }">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector="extractorName" />
        </div>
        <p class="modal-card-title">
          {{ extractor.label || extractor.name }} Extractor Configuration
        </p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <progress
          v-if="isLoadingConfigSettings || extractorLacksConfigSettings"
          class="progress is-small is-info"
        ></progress>

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
            :is-show-docs="!!extractor.docs"
            :is-show-config-warning="
              getHasPipelineWithExtractor(extractor.name)
            "
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
              :disabled="!isSaveable || isTesting || isSaving"
              @click="testConnection"
            >
              Test Connection
            </button>
          </div>
          <div class="control">
            <button
              class="button is-interactive-primary"
              :class="{
                'is-loading':
                  isLoadingConfigSettings || isInstalling || isSaving
              }"
              :disabled="!isSaveable || isTesting || isSaving"
              @click="save"
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
