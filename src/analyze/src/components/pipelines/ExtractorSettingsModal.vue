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
      return !this.getIsInstallingPlugin('extractors', this.extractorNameFromRoute) &&
             this.configSettings.settings &&
             this.configSettings.settings.length === 0;
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
        type: 'extractors',
        config: this.configSettings.config,
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
        <p class="modal-card-title">Extractor Configuration</p>
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

          <div class="field is-horizontal" v-for='setting in configSettings.settings' :key='setting.name'>
            <div class="field-label is-normal">
              <label class="label">{{ setting.label || setting.name }}</label>
              <p v-if="setting.description">{{ setting.description }}</p>
            </div>
            <div class="field-body">
              <div class="field">
                <p class="control">
                  <input
                    class="input"
                    type="text"
                    :placeholder="setting.value"
                    v-model="configSettings.config[setting.name]">
                </p>
              </div>
            </div>
          </div>

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
