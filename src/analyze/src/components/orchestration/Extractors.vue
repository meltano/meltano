<script>
import { mapState } from 'vuex';

import BaseCard from '@/components/generic/BaseCard';
import ConnectorCard from '@/components/orchestration/ConnectorCard';
import ConnectorSettings from '@/components/orchestration/ConnectorSettings';

import orchestrationsApi from '@/api/orchestrations';

export default {
  name: 'Extractors',
  components: {
    BaseCard,
    ConnectorCard,
    ConnectorSettings,
  },
  data() {
    return {
      filterExtractorsText: '',
      installingExtractor: false,
      extractorInFocus: null,
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapState('orchestrations', [
      'installedPlugins',
      'extractors',
    ]),
    getIsConnectorInstalled() {
      return extractor => this.installedPlugins.extractors.find(item => item.name === extractor);
    },
    filteredExtractors() {
      if (this.filterExtractorsText) {
        return this.extractors
          .filter(item => item.indexOf(this.filterExtractorsText) > -1);
      }
      return this.extractors;
    },
  },
  methods: {
    installExtractor(extractor) {
      this.installingExtractor = true;

      orchestrationsApi.addExtractors({
        name: extractor,
      }).then((response) => {
        if (response.status === 200) {
          this.$store.dispatch('orchestrations/getInstalledPlugins')
            .then(() => {
              this.installingExtractor = false;
            });
        }
      });
    },
    updateExtractorInFocus(extractor) {
      const extractorObj = this.installedPlugins.extractors.find(item => item.name === extractor);
      this.extractorInFocus = extractorObj;
    },
  },
};
</script>

<template>
  <div>
    <div v-if='extractorInFocus'>
      <div class="columns">
        <div class="column">
          <h2>Extractor Settings</h2>
        </div>
        <div class="column">
          <div class="buttons is-pulled-right">
            <button
              class="button is-outlined"
              @click="updateExtractorInFocus(null)">Back</button>
          </div>
        </div>
      </div>

      <ConnectorSettings
        :extractor='extractorInFocus'
      ></ConnectorSettings>

    </div>

    <div v-else>

      <div
        v-if="filteredExtractors.length === 0"
        class='content'>
        <p>
          No extractors are available.
        </p>
      </div>

      <template v-else>
        <div class="columns">
          <div class="column is-4 is-offset-4">
            <input
              type="text"
              v-model="filterExtractorsText"
              placeholder="Filter extractors..."
              class="input connector-input">
          </div>
        </div>

        <div class="tile is-ancestor flex-and-wrap">
          <div
            class="tile is-parent is-3"
            v-for="(extractor, index) in filteredExtractors"
            :key="`${extractor}-${index}`">
            <div class="tile is-child box">
              <div class="image is-64x64 container">
                <img
                  :class='{ "grayscale": !getIsConnectorInstalled(extractor) }'
                  :src="`/static/logos/${extractor.replace('tap-', '')}-logo.png`"
                  :alt="`gitlab logo`">
              </div>
              <div class="content is-small">
                <p class='has-text-centered'>
                  {{extractor}}
                </p>

                <template v-if='getIsConnectorInstalled(extractor)'>
                  <div class="buttons are-small">
                    <a
                      class='button is-success flex-grow-1'
                      @click="updateExtractorInFocus(extractor)">Account Settings</a>
                    <a class='button' disabled>Uninstall</a>
                  </div>
                </template>
                <template v-else>
                  <a
                    class="button is-success is-outlined is-block is-small"
                    @click="installExtractor(extractor)">Install</a>
                </template>

              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
