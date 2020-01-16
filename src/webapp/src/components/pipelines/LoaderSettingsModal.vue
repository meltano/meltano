<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import lodash from 'lodash'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'
import ConnectorSettingsDropdown from '@/components/pipelines/ConnectorSettingsDropdown'
import utils from '@/utils/utils'

export default {
  name: 'LoaderSettingsModal',
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
      'getIsInstallingPlugin',
      'getPluginProfiles'
    ]),
    ...mapGetters('orchestration', ['getHasValidConfigSettings']),
    ...mapState('orchestration', ['loaderInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),
    isInstalled() {
      return this.getIsPluginInstalled('loaders', this.loaderName)
    },
    isInstalling() {
      return this.getIsInstallingPlugin('loaders', this.loaderName)
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
        this.loader.settingsGroupValidation
      )
      return this.isInstalled && isValid
    },
    loader() {
      return this.getInstalledPlugin('loaders', this.loaderName)
    },
    requiredSettingsKeys() {
      return utils.requiredConnectorSettingsKeys(
        this.localConfiguration.settings,
        this.loader.settingsGroupValidation
      )
    }
  },
  created() {
    this.loaderName = this.$route.params.loader
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      const needsInstallation = this.loader.name !== this.loaderName
      const addConfig = {
        pluginType: 'loaders',
        name: this.loaderName
      }

      const uponPlugin = needsInstallation
        ? this.addPlugin(addConfig).then(() => {
            this.getLoaderConfiguration().then(this.createEditableConfiguration)
            this.installPlugin(addConfig)
          })
        : this.getLoaderConfiguration().then(this.createEditableConfiguration)

      uponPlugin.catch(err => {
        this.$error.handle(err)
        this.close()
      })
    })
  },
  beforeDestroy() {
    this.$store.dispatch('orchestration/resetLoaderInFocusConfiguration')
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'loaders' })
      }
    },
    createEditableConfiguration() {
      this.localConfiguration = Object.assign(
        { profileInFocusIndex: 0 },
        lodash.cloneDeep(this.loaderInFocusConfiguration)
      )
    },
    getLoaderConfiguration() {
      return this.$store.dispatch(
        'orchestration/getLoaderConfiguration',
        this.loaderName
      )
    },
    saveConfigAndGoToSchedule() {
      this.$store
        .dispatch('orchestration/savePluginConfiguration', {
          name: this.loader.name,
          type: 'loaders',
          profiles: this.localConfiguration.profiles
        })
        .then(() => {
          this.$store.dispatch('orchestration/updateRecentELTSelections', {
            type: 'loader',
            value: this.loader
          })
          this.$router.push({ name: 'schedules' })
          Vue.toasted.global.success(`Connector Saved - ${this.loader.name}`)
        })
        .catch(err => {
          this.$error.handle(err)
          this.close()
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
          <ConnectorLogo :connector="loaderName" />
        </div>
        <p class="modal-card-title">Loader Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>

      <section class="modal-card-body is-overflow-y-scroll">
        <div v-if="isLoadingConfigSettings || isInstalling" class="content">
          <div v-if="!isLoadingConfigSettings && isInstalling" class="level">
            <div class="level-item">
              <p class="is-italic">
                Installing {{ loader.label }} can take up to a minute.
              </p>
            </div>
          </div>
          <progress class="progress is-small is-info"></progress>
        </div>

        <template v-if="!isLoadingConfigSettings">
          <div v-if="loader.signupUrl" class="mb1r">
            <p>
              This plugin requires an account. If you don't have one, you can
              <a :href="loader.signupUrl" target="_blank">sign up here</a>.
            </p>
          </div>
          <!--
            TEMP ConnectorSettingsDropdown removal from UI.
            Conditional removal so existing users with 2+ profiles already created still can access them
            Get context here https://gitlab.com/meltano/meltano/issues/1389.
          -->
          <template v-if="localConfiguration.profiles.length > 1">
            <ConnectorSettingsDropdown
              :connector="loader"
              plugin-type="loaders"
              :config-settings="localConfiguration"
            ></ConnectorSettingsDropdown>
          </template>

          <ConnectorSettings
            field-class="is-small"
            :config-settings="localConfiguration"
            :plugin="loader"
            :required-settings-keys="requiredSettingsKeys"
          />
        </template>
      </section>

      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!isSaveable"
          @click.prevent="saveConfigAndGoToSchedule"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss" scoped></style>
