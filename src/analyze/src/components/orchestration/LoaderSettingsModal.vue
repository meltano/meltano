<template>

  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <img
            :src='getLoaderImageUrl(loaderNameFromRoute)'
            :alt="`${getLoaderNameWithoutPrefixedTargetDash(loaderNameFromRoute)} logo`">
        </div>
        <p class="modal-card-title">Loader Settings</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <template v-if='getIsInstallingLoaderPlugin(loaderNameFromRoute)'>
          <div class="content">
            <div class="level">
              <div class="level-item">
                <p>Installing {{loaderNameFromRoute}} can take up to a minute.</p>
              </div>
            </div>
            <progress class="progress is-small is-info"></progress>
          </div>
        </template>

        <template v-if='configSettings'>

          <div class="field is-horizontal" v-for='(val, key) in configSettings' :key='key'>
            <div class="field-label is-normal">
              <label class="label">{{key}}</label>
            </div>
            <div class="field-body">
              <div class="field">
                <p class="control">
                  <input
                    class="input"
                    type="text"
                    :placeholder="val"
                    v-model="configSettings[key]">
                </p>
              </div>
            </div>
          </div>

          <article class="message is-warning is-small">
            <div class="message-header">
              <p>Warning</p>
            </div>
            <div class="message-body">
              <p>These connector settings are not currently persisted on the backend. Additionally, this UI still needs further iteration from a UX lens.</p>
            </div>
          </article>

        </template>

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
<script>
import { mapState, mapGetters } from 'vuex';

import _ from 'lodash';

export default {
  name: 'LoaderSettingsModal',
  created() {
    this.loaderNameFromRoute = this.$route.params.loader;
    this.$store.dispatch('configuration/getLoaderConfiguration', this.loaderNameFromRoute);
    this.$store.dispatch('configuration/getInstalledPlugins');
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/clearLoaderInFocusConfiguration');
  },
  computed: {
    ...mapGetters('configuration', [
      'getLoaderImageUrl',
      'getLoaderNameWithoutPrefixedTargetDash',
      'getIsPluginInstalled',
      'getIsInstallingLoaderPlugin',
    ]),
    ...mapState('configuration', [
      'installedPlugins',
      'loaderInFocusConfiguration',
    ]),
    configSettings() {
      return this.loader.config
        ? Object.assign(this.loader.config, this.loaderInFocusConfiguration)
        : this.loaderInFocusConfiguration;
    },
    isSaveable() {
      const hasOwns = [];
      _.forOwn(this.configSettings, val => hasOwns.push(val));
      return hasOwns.length > 0 && this.getIsPluginInstalled(this.loaderNameFromRoute);
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
        type: 'loader',
        config: this.configSettings,
      });
      this.$router.push({ name: 'orchestration' });
    },
  },
};
</script>
