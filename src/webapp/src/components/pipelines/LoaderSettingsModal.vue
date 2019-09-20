<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'

export default {
  name: 'LoaderSettingsModal',
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
    ...mapState('configuration', ['loaderInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),
    isInstalled() {
      return this.getIsPluginInstalled('loaders', this.loaderNameFromRoute)
    },
    isInstalling() {
      return this.getIsInstallingPlugin('loaders', this.loaderNameFromRoute)
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.loaderInFocusConfiguration,
        'config'
      )
    },
    isSaveable() {
      const isValid = this.getHasValidConfigSettings(
        this.loaderInFocusConfiguration,
        this.loader.settingsGroupValidation
      )
      return !this.isInstalling && this.isInstalled && isValid
    },
    loader() {
      return this.getInstalledPlugin('loaders', this.loaderNameFromRoute)
    }
  },
  created() {
    this.loaderNameFromRoute = this.$route.params.loader
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      const needsInstallation = this.loader.name !== this.loaderNameFromRoute
      if (needsInstallation) {
        const config = {
          pluginType: 'loaders',
          name: this.loaderNameFromRoute
        }
        this.addPlugin(config).then(() => {
          this.prepareLoaderConfiguration()
          this.installPlugin(config)
        })
      } else {
        this.prepareLoaderConfiguration()
      }
    })
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/resetLoaderInFocusConfiguration')
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
    prepareLoaderConfiguration() {
      this.$store.dispatch(
        'configuration/getLoaderConfiguration',
        this.loaderNameFromRoute
      )
    },
    saveConfigAndGoToTransforms() {
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          name: this.loader.name,
          type: 'loaders',
          config: this.loaderInFocusConfiguration.config
        })
        .then(() => {
          this.$store.dispatch('configuration/updateRecentELTSelections', {
            type: 'loader',
            value: this.loader
          })
          this.$router.push({ name: 'transforms' })
          Vue.toasted.global.success(`Connector Saved - ${this.loader.name}`)
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
          <ConnectorLogo :connector="loaderNameFromRoute" />
        </div>
        <p class="modal-card-title">Loader Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>

      <section class="modal-card-body">
        <div v-if="isLoadingConfigSettings || isInstalling" class="content">
          <div v-if="!isLoadingConfigSettings && isInstalling" class="level">
            <div class="level-item">
              <p class="is-italic">
                Installing {{ loaderNameFromRoute }} can take up to a minute.
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
          <ConnectorSettings
            field-class="is-small"
            :config-settings="loaderInFocusConfiguration"
          />
          <div v-if="loader.docs" class="content has-text-centered mt1r">
            <p>
              View Meltano's
              <a :href="loader.docs" target="_blank" class="has-text-underlined"
                >{{ loaderNameFromRoute }} docs</a
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
          @click.prevent="saveConfigAndGoToTransforms"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss" scoped></style>
