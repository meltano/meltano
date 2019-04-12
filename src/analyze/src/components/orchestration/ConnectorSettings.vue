<template>
  <div>

    <div class="columns">
      <div class="column">
        <h3>Extractor Connection Settings</h3>
      </div>
      <div class="column is-2">
          <div class="buttons is-pulled-right">
            <button
              class='button is-success'
              :disabled="!hasConfig"
              @click='saveConfig'>Save</button>
          </div>
        </div>
    </div>

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

  </div>
</template>

<script>
import _ from 'lodash';

export default {
  name: 'ConnectorSettings',
  data() {
    return {
      configSettings: {},
    };
  },
  props: {
    extractor: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  created() {
    this.configSettings = Object.assign({}, this.extractor.config);
  },
  computed: {
    hasConfig() {
      const hasOwns = [];
      _.forOwn(this.configSettings, val => hasOwns.push(val));
      return hasOwns.length > 0;
    },
  },
  methods: {
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
