<script>
import { mapState, mapGetters } from 'vuex';
import ConnectorLogo from '@/components/generic/ConnectorLogo';
import ConnectorSettings from '@/components/pipelines/ConnectorSettings';

export default {
  name: 'LoaderSettingsModal',
  components: {
    ConnectorLogo,
    ConnectorSettings,
  },
  created() {
    this.loaderNameFromRoute = this.$route.params.loader;
    this.$store.dispatch('configuration/getLoaderConfiguration', this.loaderNameFromRoute);
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/clearLoaderInFocusConfiguration');
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
      'loaderInFocusConfiguration',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
    ]),
    configSettings() {
      return this.loader.config
        ? Object.assign(this.loader.config, this.loaderInFocusConfiguration)
        : this.loaderInFocusConfiguration;
    },
    isLoading() {
      return !Object.prototype.hasOwnProperty.call(this.configSettings, 'config');
    },
    isSaveable() {
      const isInstalling = this.getIsInstallingPlugin('loaders', this.loaderNameFromRoute);
      const isInstalled = this.getIsPluginInstalled('loaders', this.loaderNameFromRoute);
      const isValid = this.getHasValidConfigSettings(this.configSettings);
      return !isInstalling && isInstalled && isValid;
    },
    loader() {
      const targetLoader = this.installedPlugins.loaders
        ? this.installedPlugins.loaders.find(item => item.name === this.loaderNameFromRoute)
        : null;
      return targetLoader || {};
    },
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'loaders' });
      }
    },
    saveConfigAndGoToOrchestration() {
      this.$store.dispatch('configuration/saveLoaderConfiguration', {
        name: this.loader.name,
        type: 'loaders',
        config: this.configSettings.config,
      }).then(() => {
        this.$router.push({ name: 'schedules' });
      });
    },
  },
};
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-narrow">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector='loaderNameFromRoute' />
        </div>
        <p class="modal-card-title">Loader Configuration</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>

      <section class="modal-card-body">

        <template v-if='getIsInstallingPlugin("loaders", loaderNameFromRoute)'>
          <div class="content">
            <div class="level">
              <div class="level-item">
                <p>Installing {{loaderNameFromRoute}} can take up to a minute.</p>
              </div>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </template>
        <progress
          v-else-if='isLoading'
          class="progress is-small is-info"></progress>

        <ConnectorSettings
          v-if='!isLoading && configSettings'
          :config-settings='configSettings'/>

      </section>

      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          class='button is-interactive-primary'
          :disabled='!isSaveable'
          @click.prevent="saveConfigAndGoToOrchestration">Save</button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss">
</style>
