<script>
import { mapGetters, mapState } from 'vuex';

import ConnectorLogo from '@/components/generic/ConnectorLogo';

import _ from 'lodash';

export default {
  name: 'ExtractorSettingsModal',
  components: {
    ConnectorLogo,
  },
  created() {
    this.extractorNameFromRoute = this.$route.params.extractor;
    this.$store.dispatch('configuration/getExtractorConfiguration', this.extractorNameFromRoute);
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  beforeDestroy() {
    this.$store.dispatch('configuration/clearExtractorInFocusConfiguration');
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'getIsInstallingPlugin',
    ]),
    ...mapState('configuration', [
      'extractorInFocusConfiguration',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
    ]),
    configSettings() {
      return this.extractor.config
        ? Object.assign(this.extractor.config, this.extractorInFocusConfiguration)
        : this.extractorInFocusConfiguration;
    },
    extractorLacksConfigSettingsAndIsInstalled() {
      return this.configSettings === null &&
        !this.getIsInstallingPlugin('extractors', this.extractorNameFromRoute);
    },
    extractor() {
      const targetExtractor = this.installedPlugins.extractors
        ? this.installedPlugins.extractors.find(item => item.name === this.extractorNameFromRoute)
        : null;
      return targetExtractor || {};
    },
    isSaveable() {
      const hasOwns = [];
      _.forOwn(this.configSettings, val => hasOwns.push(val));
      return hasOwns.length > 0 && this.getIsPluginInstalled('extractors', this.extractorNameFromRoute);
    },
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'extractors' });
      }
    },
    beginEntitySelection() {
      this.$router.push({ name: 'extractorEntities', params: { extractor: this.extractor.name } });
    },
    saveConfigAndBeginEntitySelection() {
      this.$store.dispatch('configuration/saveExtractorConfiguration', {
        name: this.extractor.name,
        type: 'extractor',
        config: this.configSettings,
      });
      this.beginEntitySelection();
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
          <ConnectorLogo :connector='extractorNameFromRoute' />
        </div>
        <p class="modal-card-title">Extractor Settings</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

        <template v-if='getIsInstallingPlugin("extractors", extractorNameFromRoute)'>
          <div class="content">
            <div class="level">
              <div class="level-item">
                <p>Installing {{extractorNameFromRoute}} can take up to a minute.</p>
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

        <template v-if='extractorLacksConfigSettingsAndIsInstalled'>
          <div class="content">
            <p>{{extractorNameFromRoute}} doesn't require configuration.</p>
            <ul>
              <li>Click "Next" to advance</li>
              <li>Click "Cancel" to install other extractors</li>
            </ul>
          </div>
        </template>

      </section>
      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          v-if='extractorLacksConfigSettingsAndIsInstalled'
          class='button is-interactive-primary'
          @click='saveConfigAndBeginEntitySelection'>Next</button>
        <button
          v-else
          class='button is-interactive-primary'
          :disabled="!isSaveable"
          @click='saveConfigAndBeginEntitySelection'>Save</button>
      </footer>
    </div>
  </div>

</template>

<style lang="scss">
</style>
