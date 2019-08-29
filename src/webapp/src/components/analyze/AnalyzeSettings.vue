<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ConnectorSettings from '@/components/pipelines/ConnectorSettings'
import Message from '@/components/generic/Message'

export default {
  name: 'AnalyzeSettings',
  components: {
    ConnectorLogo,
    ConnectorSettings,
    Message
  },
  data() {
    return {
      connectionName: null,
      isSavingConfiguration: false
    }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin', 'getIsInstallingPlugin', 'getIsPluginInstalled']),
    ...mapGetters('configuration', ['getHasValidConfigSettings']),
    ...mapState('configuration', ['connectionInFocusConfiguration']),
    ...mapState('plugins', ['plugins', 'installedPlugins']),
    connection() {
      return this.getInstalledPlugin('connections', this.connectionName)
    },
    isSaveable() {
      const isInstalling = this.getIsInstallingPlugin(
        'connections',
        this.connectionName
      )
      const isInstalled = this.getIsPluginInstalled(
        'connections',
        this.connectionName
      )
      const isValid = this.getHasValidConfigSettings(
        this.connectionInFocusConfiguration, this.connection.settingsGroupValidation
      )
      return !isInstalling && isInstalled && isValid
    }
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/resetConnectionInFocusConfiguration')
  },
  methods: {
    ...mapActions('configuration', ['getConnectionConfiguration']),
    configureConnection(connection) {
      this.$store
        .dispatch('plugins/addPlugin', {
          pluginType: 'connections',
          name: connection
        })
        .then(() => {
          this.connectionName = connection
          this.getConnectionConfiguration(connection)
        })
    },
    saveConfig() {
      this.isSavingConfiguration = true
      this.$store
        .dispatch('configuration/savePluginConfiguration', {
          type: 'connections',
          name: this.connection.name,
          config: this.connectionInFocusConfiguration.config
        })
        .then(() => {
          this.isSavingConfiguration = false
          Vue.toasted.global.success(
            `Connection Saved - ${this.connection.name}`
          )
        })
    }
  }
}
</script>

<template>
  <section class="columns">
    <div class="column is-one-third">
      <h2 class="title is-5">Available Connections</h2>
      <div class="tile is-ancestor is-flex is-flex-column">
        <div
          v-for="(pluginConnection, index) in plugins.connections"
          :key="`${pluginConnection}-${index}`"
          class="tile is-parent is-flex-no-grow"
        >
          <div class="tile level box">
            <div class="level-left">
              <div class="level-item is-flex-column has-text-left">
                <ConnectorLogo
                  class="connector-logo"
                  :connector="pluginConnection"
                  :is-grayscale="
                    !getIsPluginInstalled('connections', pluginConnection)
                  "
                />
              </div>
            </div>
            <div class="level-right">
              <div class="level-item content is-small is-flex-column">
                <p class="is-uppercase has-text-weight-bold">
                  {{ pluginConnection }}
                </p>
                <div class="buttons are-small">
                  <a
                    class="button is-interactive-primary flex-grow-1"
                    @click="configureConnection(pluginConnection)"
                    >Configure</a
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="connectionInFocusConfiguration" class="column" rel="container">
      <h2 class="title is-5">Configuration</h2>
      <ConnectorSettings
        v-if="connectionName"
        class="box"
        :config-settings="connectionInFocusConfiguration"
      >
        <section slot="bottom" class="field buttons is-right">
          <button
            class="button is-interactive-primary"
            :class="{ 'is-loading': isSavingConfiguration }"
            :disabled="!isSaveable"
            @click.prevent="saveConfig"
          >
            Save
          </button>
        </section>
      </ConnectorSettings>
      <div v-else class="box">
        <div class="content">
          <Message>
            <p>This manual connection requirement will soon be automated :)</p>
          </Message>

          <p>
            After successfully setting up a
            <router-link :to="{ name: 'schedules' }">data pipeline</router-link>
            Meltano has:
          </p>
          <ol>
            <li>
              <em>Extracted</em> data <em>from</em> a database or API (data
              source)
            </li>
            <li>
              <em>Loaded</em> the extracted data <em>to</em> a database
              (warehouse)
            </li>
            <li>
              <em>Transformed</em> the loaded data <em>to</em> the warehouse
              under a special <em>analytics schema</em>
            </li>
          </ol>
          <p>
            Now Meltano needs a connection to that <em>analytics schema</em> so
            Meltano Analyze can connect and query. Use the options to the left
            to setup the Analyze connection.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
.connector-logo {
  max-height: 48px;
  object-fit: scale-down;
}
</style>
