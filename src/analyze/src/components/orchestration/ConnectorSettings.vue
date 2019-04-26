<template>
  <div>

    <div class="columns">

      <div class="column box is-4 is-offset-4">
        <article class="media">
          <figure class="media-left">
            <p class="image is-64x64">
              <img :src='imageUrl' :alt="`${extractor.name} logo`">
            </p>
          </figure>
          <div class="media-content">
            <div class="content">
              <p>
                <span class='has-text-weight-bold'>Connector Settings</span>
                <br>
                {{extractor.name}}
              </p>
            </div>
          </div>
        </article>

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

        <div class="buttons is-pulled-right">
          <button
            class="button"
            @click="clearExtractorInFocus()">Cancel</button>
          <button
            class='button is-success'
            :disabled="!hasConfig"
            @click='saveConfig'>Save</button>
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
    imageUrl: {
      type: String,
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
    clearExtractorInFocus() {
      this.$emit('clearExtractorInFocus');
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
