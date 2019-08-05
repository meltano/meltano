<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import ConnectorLogo from '@/components/generic/ConnectorLogo';
import ConnectorSettings from '@/components/pipelines/ConnectorSettings';


export default {
  name: 'AnalyzeSettings',
  data() {
    return {
      connectionName: null,
    };
  },
  components: {
    ConnectorLogo,
    ConnectorSettings,
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins');
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/clearConnectionInFocusConfiguration');
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'getIsInstallingPlugin',
    ]),
    ...mapGetters('configuration', [
      'getHasValidConfigSettings',
    ]),
    ...mapState('configuration', [
      'connectionInFocusConfiguration',
    ]),
    ...mapState('plugins', [
      'plugins',
      'installedPlugins',
    ]),
    connection() {
      const targetConnection = this.installedPlugins.connections
        ? this.installedPlugins.connections.find(item => item.name === this.connectionName)
        : null;
      return targetConnection || {};
    },
    configSettings() {
      return this.connection.config
        ? Object.assign(this.connection.config, this.connectionInFocusConfiguration)
        : this.connectionInFocusConfiguration;
    },
    isSaveable() {
      const isInstalling = this.getIsInstallingPlugin('connections', this.connectionName);
      const isInstalled = this.getIsPluginInstalled('connections', this.connectionName);
      const isValid = this.getHasValidConfigSettings(this.configSettings);
      return !isInstalling && isInstalled && isValid;
    },
  },
  methods: {
    ...mapActions('configuration', [
      'getConnectionConfiguration',
    ]),
    configureConnection(connection) {
      this.$store.dispatch('plugins/addPlugin', {
        pluginType: 'connections',
        name: connection,
      }).then(() => {
        this.connectionName = connection;
        this.getConnectionConfiguration(connection);
      });
    },
    saveConfig() {
      this.$store.dispatch('configuration/savePluginConfiguration', {
        type: 'connections',
        name: this.connection.name,
        config: this.configSettings.config,
      });
    },
  },
};
</script>

<template>
  <section class="columns">
    <div class="column is-one-third">
      <h2 class="title is-5">Available Connections</h2>
      <div class="tile is-ancestor is-flex is-flex-column">
        <div class="tile is-parent is-flex-no-grow"
             v-for="(connection, index) in plugins.connections"
             :key="`${connection}-${index}`">
          <div class="tile level box">
            <div class="level-left">
              <div class="level-item is-flex-column has-text-left">
                <ConnectorLogo class="connector-logo"
                               :connector='connection'
                               :is-grayscale='!getIsPluginInstalled("connections", connection)' />
              </div>
            </div>
            <div class="level-right">
              <div class="level-item content is-small is-flex-column">
                <p class="is-uppercase has-text-weight-bold">{{ connection }}</p>
                <div class="buttons are-small">
                  <a class="button is-interactive-primary flex-grow-1"
                     @click="configureConnection(connection)">Configure</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="column" rel="container" v-if="configSettings">
      <h2 class="title is-5">Configuration</h2>
      <ConnectorSettings v-if='connectionName'
                         class="box"
                         :config-settings='configSettings'>
        <section class="field buttons is-right"
                 slot="bottom">
          <button class='button is-interactive-primary'
                  :disabled='!isSaveable'
                  @click.prevent="saveConfig">Save</button>
        </section>
      </ConnectorSettings>
      <div v-else
           class="box">
        <div class="content">
          <article class="message is-info">
            <div class="message-header">
              <a class="button is-borderless has-background-transparent has-text-white">
                <span class="icon">
                  <font-awesome-icon icon="info-circle"></font-awesome-icon>
                </span>
                <span>Info</span>
              </a>
            </div>
            <div class="message-body">
              <p>This manual connection requirement will soon be automated :)</p>
            </div>
          </article>
          <p>After successfully setting up a <router-link :to='{ name: "schedules" }'>data pipeline</router-link> Meltano has:</p>
          <ol>
            <li><em>Extracted</em> data <em>from</em> a database or API (data source)</li>
            <li><em>Loaded</em> the extracted data <em>to</em> a database (warehouse)</li>
            <li><em>Transformed</em> the loaded data <em>to</em> the warehouse under a special <em>analytics schema</em></li>
          </ol>
          <p>Now Meltano needs a connection to that <em>analytics schema</em> so Meltano Analyze can connect and query. Use the options to the left to setup the Analyze connection.</p>
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
