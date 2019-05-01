<template>

  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <div class="modal-card-head-image image is-64x64 level-item">
          <img
            :src='getExtractorImageUrl(extractorNameFromRoute)'
            :alt="`${getExtractorNameWithoutPrefixedTapDash(extractorNameFromRoute)} logo`">
        </div>
        <p class="modal-card-title">Extractor Settings</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">

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

      </section>
      <footer class="modal-card-foot buttons is-right">
        <button
          class="button"
          @click="close">Cancel</button>
        <button
          class='button is-interactive-primary'
          :disabled="!hasConfig"
          @click='saveConfig'>Save</button>
      </footer>
    </div>
  </div>

</template>

<script>
import { mapGetters, mapState } from 'vuex';

import _ from 'lodash';

export default {
  name: 'ExtractorSettingsModal',
  created() {
    this.extractorNameFromRoute = this.$route.params.extractor;
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('orchestrations', [
      'getExtractorImageUrl',
      'getExtractorNameWithoutPrefixedTapDash',
    ]),
    ...mapState('orchestrations', [
      'installedPlugins',
    ]),
    configSettings() {
      return this.extractor ? Object.assign({}, this.extractor.config) : {};
    },
    extractor() {
      return this.installedPlugins.extractors
        ? this.installedPlugins.extractors.find(item => item.name === this.extractorNameFromRoute)
        : {};
    },
    hasConfig() {
      const hasOwns = [];
      _.forOwn(this.configSettings, val => hasOwns.push(val));
      return hasOwns.length > 0;
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
    saveConfig() {
      this.$store.dispatch('orchestrations/saveExtractorConfiguration', {
        extractorName: this.extractor.name,
        config: this.configSettings,
      });
    },
  },
};
</script>

<style lang="scss">
</style>
