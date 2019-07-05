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
  <section class="columns">
    <div class="column is-one-third is-ancestor flex-and-wrap flex-column">
      <h2 class="title is-5">Available Connections</h2>
      <div class="tile is-parent no-grow"
	   v-for="(connection, index) in plugins.connections"
	   :key="`${connection}-${index}`">
	<div class="tile level box">
	  <div class="level-left">
	    <div class="image level-item is-48x48">
	      <ConnectorLogo
		:connector='connection'
		:is-grayscale='!getIsPluginInstalled("connections", connection)' />
	    </div>
	  </div>
	  <span class="level-item">{{ connection }}</span>
	  <div class="level-right">
	    <div class="level-item content is-small">
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
    </div>
    
    <div class="column is-two-third" rel="container" v-if="configSettings">
      <h2 class="title is-5">Configuration</h2>
      <div class="box">
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
	  :config-settings='configSettings' />
	
	<section class="buttons is-right">
	  <button
	    class="button"
	    @click="close">Cancel</button>
	  <button
	    class='button is-interactive-primary'
	    :disabled='!isSaveable'
	    @click.prevent="saveConfig">Save</button>
	</section>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
  .no-grow {
    flex-grow: 0;
  }

  .flex-column {
    flex-direction: column;
  }
</style>
