<script>
 import { mapState, mapGetters, mapActions } from 'vuex';
 import ConnectorLogo from '@/components/generic/ConnectorLogo';
 import ConnectorSettings from '@/components/pipelines/ConnectorSettings';


 export default {
   name: 'AnalyzeSettings',
   data() {
     return {
       model: { profile: null }
     }
   },
   components: {
     ConnectorLogo,
     ConnectorSettings,
   },
   created() {
     this.connectionNameFromRoute = 'sqlite'; // this.$route.params.connection;

     this.$store.dispatch('plugins/getAllPlugins');
     this.$store.dispatch('plugins/getInstalledPlugins');
     this.$store.dispatch('configuration/getConnectionConfiguration', this.connectionNameFromRoute);
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
                              ? this.installedPlugins.connections.find(item => item.name === this.connectionNameFromRoute)
                              : null;
       return targetConnection || {};
     },
     configSettings() {
       return this.connection.config
            ? Object.assign(this.connection.config, this.connectionInFocusConfiguration)
            : this.connectionInFocusConfiguration;
     },
     isSaveable() {
       const isInstalling = this.getIsInstallingPlugin('connections', this.connectionNameFromRoute);
       const isInstalled = this.getIsPluginInstalled('connections', this.connectionNameFromRoute);
       const isValid = this.getHasValidConfigSettings(this.configSettings);
       return !isInstalling && isInstalled && isValid;
     },
   },
   methods: {
     ...mapActions('configuration', [
       'getConnectionConfiguration',
     ]),
     close() {
       if (this.prevRoute) {
         this.$router.go(-1);
       } else {
         this.$router.push({ name: 'connections' });
       }
     },
     installConnection(connection) {
       this.$store.dispatch('plugins/addPlugin', { pluginType: 'connections', name: connection })
           .then(this.getConnectionConfiguration(connection))
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
  <section>
    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
               v-for="(connection, index) in plugins.connections"
               :key="`${connection}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo
              :connector='connection'
              :is-grayscale='!getIsPluginInstalled("connections", connection)' />
          </div>
          <div class="content is-small">
            <p class="has-text-centered">
              {{ connection }}
            </p>

            <div class="buttons are-small">
              <a v-if="!getIsPluginInstalled('connections', connection)"
                 class="button is-interactive-primary flex-grow-1"
                 @click="installConnection(connection)">Install</a>

              <a v-else
                 class="button is-interactive-primary flex-grow-1"
                 @click="getConnectionConfiguration(connection)">Configure</a>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <template v-if="configSettings">
      <h2>Connection Configuration</h2>
      <div v-if='getIsInstallingPlugin("connections", connectionNameFromRoute)'>
        class="content">
        <div class="level">
          <div class="level-item">
            <p>Installing {{connectionNameFromRoute}} can take up to a minute.</p>
          </div>
        </div>
        <progress class="progress is-small is-info"></progress>
      </div>
      
      <ConnectorSettings
        v-if='configSettings'
              :config-settings='configSettings'>
        <div class="field is-horizontal">
          <div class="field-label is-normal">
            <label class="label is-small">Profile name</label>
          </div>
          <div class="field-body">
            <div class="field">
              <p class="control is-expanded">
                <input type="text"
                       class="input is-small"
                       v-model="model.profile" />
              </p>
            </div>
          </div>
        </div>
      </ConnectorSettings>
      
      <section>
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          class='button is-interactive-primary'
          :disabled='!isSaveable'
	  @click.prevent="saveConfig">Save</button>
      </section>

    </template>
  </section>
</template>

<style lang="scss">
</style>
