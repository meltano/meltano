<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import ConnectorSettings from '@/components/pipelines/ConnectorSettings'
import utils from '@/utils/utils'

export default {
  name: 'PluginSettingsModal',
  components: {
    ConnectorSettings,
  },
  props: {
    pluginType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      isSaving: false,
      isTesting: false,
      localConfiguration: {},
      uploadFormData: null,
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'getInstalledPlugin',
      'getIsPluginInstalled',
      'getIsInstallingPlugin',
    ]),
    ...mapGetters('orchestration', [
      'getHasPipelineWithPlugin',
      'getHasValidConfigSettings',
    ]),
    ...mapState('orchestration', ['pluginInFocusConfiguration']),

    getHasPipeline() {
      return this.getHasPipelineWithPlugin(
        this.singularizedType,
        this.plugin.name
      )
    },
    pluginLacksConfigSettings() {
      return (
        this.localConfiguration.settings &&
        this.localConfiguration.settings.length === 0
      )
    },
    plugin() {
      return this.getInstalledPlugin(this.pluginType, this.pluginName)
    },
    isInstalled() {
      return this.getIsPluginInstalled(this.pluginType, this.pluginName)
    },
    isInstalling() {
      return this.getIsInstallingPlugin(this.pluginType, this.pluginName)
    },
    isLoader() {
      return this.pluginType === 'loaders'
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.localConfiguration,
        'config'
      )
    },
    isSaveable() {
      if (this.isInstalling || this.isLoadingConfigSettings) {
        return
      }
      const isValid = this.getHasValidConfigSettings(
        this.localConfiguration,
        this.localConfiguration.settingsGroupValidation
      )
      return this.isInstalled && isValid
    },
    pluginName() {
      return this.$route.params.plugin
    },
    requiredSettingsKeys() {
      return utils.requiredConnectorSettingsKeys(
        this.localConfiguration.settings,
        this.localConfiguration.settingsGroupValidation
      )
    },
    singularizedType() {
      return utils.singularize(this.pluginType)
    },
    singularizedTitledType() {
      return utils.titleCase(this.singularizedType)
    },
  },
  created() {
    this.getPluginConfiguration()
      .then(() => {
        this.createEditableConfiguration()
        this.tryAutoAdvance()
      })
      .catch((err) => {
        Vue.toasted.global.error(`Plugin ${this.pluginName} is not installed`)
        this.close()
        this.$error.handle(err)
      })
  },
  beforeDestroy() {
    this.$store.dispatch('orchestration/resetPluginInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    ...mapActions('orchestration', [
      'savePluginConfiguration',
      'testPluginConfiguration',
    ]),
    tryAutoAdvance() {
      if (this.pluginLacksConfigSettings) {
        this.save()
      }
    },
    close() {
      this.$router.push({ name: this.pluginType })
    },
    createEditableConfiguration() {
      this.localConfiguration = Object.assign(
        {},
        lodash.cloneDeep(this.pluginInFocusConfiguration)
      )
    },
    getPluginConfiguration() {
      return this.$store.dispatch(
        'orchestration/getAndFocusOnPluginConfiguration',
        { type: this.pluginType, name: this.pluginName }
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
            name: this.plugin.name,
            type: this.pluginType,
            payload: this.uploadFormData,
          })
        : Promise.resolve()

      // 2. Initialize conditional request
      uponConditionalUpload.then((response) => {
        // 2.a Update setting value with updated and secure file path
        if (response) {
          const payload = response.data
          this.localConfiguration.config[payload.settingName] = payload.path
        }

        // 3. Save config settings
        this.savePluginConfiguration({
          name: this.plugin.name,
          type: this.pluginType,
          payload: {
            config: this.localConfiguration.config,
          },
        })
          .then(() => {
            const message = this.pluginLacksConfigSettings
              ? `No configuration needed for ${this.plugin.name}`
              : `Configuration saved - ${this.plugin.name}`
            Vue.toasted.global.success(message)
            this.close()
          })
          .catch((error) => {
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
            name: this.plugin.name,
            type: this.pluginType,
            payload: { ...this.uploadFormData, tmp: true },
          })
        : Promise.resolve()

      // 2. Initialize conditional request
      uponConditionalUpload.then((response) => {
        // 2.a Update setting value with updated and secure file path
        if (response) {
          const payload = response.data
          this.localConfiguration.config[payload.settingName] = payload.path
        }

        // 3. Save config settings
        this.testPluginConfiguration({
          name: this.plugin.name,
          type: this.pluginType,
          payload: {
            config: this.localConfiguration.config,
          },
        })
          .then((response) => {
            if (response.data.isSuccess) {
              Vue.toasted.global.success(
                `Valid ${this.singularizedTitledType} Connection - ${this.plugin.name}`
              )
            } else {
              Vue.toasted.global.error(
                `Invalid ${this.singularizedTitledType} Connection - ${this.plugin.name}`
              )
            }
          })
          .then(() => {
            if (this.uploadFormData) {
              return this.$store.dispatch(
                'orchestration/deleteUploadedPluginConfigurationFile',
                {
                  name: this.plugin.name,
                  type: this.pluginType,
                  payload: {
                    ...this.uploadFormData,
                    file: null,
                    tmp: true,
                  },
                }
              )
            }
          })
          .finally(() => (this.isTesting = false))
      })
    },
  },
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div :class="{ 'modal-card': true, 'is-wide': !!plugin.docs }">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <img :src="plugin.logoUrl" alt="" />
        </div>
        <p class="modal-card-title">
          {{ plugin.label || plugin.name }}
          {{ singularizedTitledType }} Configuration
        </p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <progress
          v-if="isLoadingConfigSettings || pluginLacksConfigSettings"
          class="progress is-small is-info"
        ></progress>

        <template v-if="!isLoadingConfigSettings">
          <ConnectorSettings
            v-if="!pluginLacksConfigSettings"
            field-class="is-small"
            :config-settings="localConfiguration"
            :plugin="plugin"
            :required-settings-keys="requiredSettingsKeys"
            :upload-form-data="uploadFormData"
            :is-show-docs="!!plugin.docs"
            :is-show-config-warning="
              getHasPipeline && pluginType === 'extractors'
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
              :class="{
                'is-loading': isTesting,
                tooltip: isLoader,
                'is-tooltip-top': isLoader,
              }"
              :disabled="!isSaveable || isTesting || isSaving || isLoader"
              data-tooltip="Not available for loaders"
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
                  isLoadingConfigSettings || isInstalling || isSaving,
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
