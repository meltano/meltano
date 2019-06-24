<script>
import { mapState, mapGetters } from 'vuex';
import ConnectorLogo from '@/components/generic/ConnectorLogo';
import ConnectorSettings from '@/components/pipelines/ConnectorSettings';

import _ from 'lodash';

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
    isSaveable() {
      const hasOwns = [];
      _.forOwn(this.configSettings, val => hasOwns.push(val));
      return hasOwns.length > 0 && this.getIsPluginInstalled('loaders', this.loaderNameFromRoute);
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
      });
      this.$router.push({ name: 'schedules' });
    },
  },
};
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <ConnectorLogo :connector='loaderNameFromRoute' />
        </div>
        <p class="modal-card-title">Loader Settings</p>
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

        <ConnectorSettings
          v-if='configSettings'
          :settings='configSettings'/>

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
