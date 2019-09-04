<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'

export default {
  name: 'AnalyzeConnectionSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin']),
    ...mapGetters('configuration', ['getHasValidConfigSettings']),
    ...mapState('configuration', ['connectionInFocusConfiguration']),
    ...mapState('plugins', ['installedPlugins']),
    connectorLacksConfigSettings() {
      return (
        this.connectionInFocusConfiguration.settings &&
        this.connectionInFocusConfiguration.settings.length === 0
      )
    },
    connectorLacksConfigSettingsAndIsInstalled() {
      return !this.isInstalling && this.connectorLacksConfigSettings
    },
    connector() {
      const targetConnector = this.installedPlugins.connections
        ? this.installedPlugins.connections.find(
            item => item.name === this.connectorNameFromRoute
          )
        : null
      return targetConnector || {}
    },
    isInstalled() {
      return this.getIsPluginInstalled(
        'connections',
        this.connectorNameFromRoute
      )
    },
    isInstalling() {
      return this.getIsInstallingPlugin(
        'connections',
        this.connectorNameFromRoute
      )
    },
    isLoadingConfigSettings() {
      return !Object.prototype.hasOwnProperty.call(
        this.connectionInFocusConfiguration,
        'config'
      )
    },
    isSaveable() {
      const isValid = this.getHasValidConfigSettings(
        this.connectionInFocusConfiguration
      )
      return !this.isInstalling && this.isInstalled && isValid
    }
  },
  created() {
    this.connectorNameFromRoute = this.$route.params.connector
    this.$store.dispatch(
      'configuration/getConnectionConfiguration',
      this.connectorNameFromRoute
    )
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  beforeDestroy() {
    this.resetConnectionInFocusConfiguration()
  },
  methods: {
    ...mapActions('configuration', [
      'getConnectionConfiguration',
      'resetConnectionInFocusConfiguration'
    ]),
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'analyzeSettings' })
      }
    },
    saveConfig() {
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          name: this.connector.name,
          type: 'connections',
          config: this.connectionInFocusConfiguration.config
        })
        .then(() => {
          this.close()
          Vue.toasted.global.success(
            `Connection Saved - ${this.connector.name}`
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
          <ConnectorLogo :connector="connectorNameFromRoute" />
        </div>
        <p class="modal-card-title">Connection Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <template v-if="isInstalling">
          <div class="content">
            <div class="level">
              <div class="level-item">
                <p>
                  Installing {{ connectorNameFromRoute }} can take up to a
                  minute.
                </p>
              </div>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </template>

        <ConnectorSettings
          v-if="!isLoadingConfigSettings && !connectorLacksConfigSettings"
          field-class="is-small"
          :config-settings="connectionInFocusConfiguration"
        />

        <div v-if="connector.docs" class="mt1r">
          <p>
            Need help finding this information? We got you covered with our
            <a :href="connector.docs" target="_blank">docs here</a>.
          </p>
        </div>

        <progress
          v-if="isLoadingConfigSettings && !isInstalling"
          class="progress is-small is-info"
        ></progress>

        <template v-if="connectorLacksConfigSettingsAndIsInstalled">
          <div class="content">
            <p>{{ connectorNameFromRoute }} doesn't require configuration.</p>
            <ul>
              <li>Click "Next" to advance</li>
              <li>Click "Cancel" to install other connectors</li>
            </ul>
          </div>
        </template>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          v-if="connectorLacksConfigSettingsAndIsInstalled"
          class="button is-interactive-primary"
          @click="saveConfig"
        >
          Next
        </button>
        <button
          v-else
          class="button is-interactive-primary"
          :disabled="!isSaveable"
          @click="saveConfig"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
