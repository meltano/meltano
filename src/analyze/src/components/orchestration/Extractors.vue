<script>
import { mapState, mapGetters } from 'vuex';

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
      'extractorSettings',
    ]),
    ...mapGetters('orchestrations', [
      'remainingExtractors',
    ]),
    filteredExtractors() {
      if (this.filterExtractorsText) {
        return this.remainingExtractors
          .filter(item => item.indexOf(this.filterExtractorsText) > -1);
      }
      return this.remainingExtractors;
    },
    filteredInstalledExtractors() {
      if (this.installedPlugins) {
        if (this.filterExtractorsText) {
          return this.installedPlugins.extractors
            .filter(item => item.name.indexOf(this.filterExtractorsText) > -1);
        }
        return this.installedPlugins.extractors;
      }
      return [];
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
      this.extractorInFocus = extractor;
    },
  },
}
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
      <input
        type="text"
        v-model="filterExtractorsText"
        placeholder="Filter extractors..."
        class="input connector-input">
      <h2 class="title is-3">Installed</h2>
      <p v-if="!filteredInstalledExtractors || filteredInstalledExtractors.length < 1">
        No extractors currently installed
      </p>
      <div class="installed-connectors">
        <ConnectorCard v-for="extractor in filteredInstalledExtractors"
          :connector="extractor.name"
          :key="`${extractor.name}`"
        >
          <template v-slot:callToAction>
            <button
              @click="updateExtractorInFocus(extractor)"
              class="card-button">Settings</button>
          </template>
        </ConnectorCard>
      </div>

      <h2 class="title is-3">Available</h2>
      <p v-if="installingExtractor">Installing...</p>
      <progress v-if="installingExtractor" class="progress is-small is-info"></progress>
      <p v-if="filteredExtractors.length === 0">
        All available extractors have been installed.
      </p>
      <div v-else class="card-grid">
        <ConnectorCard v-for="(extractor, index) in filteredExtractors"
          :connector="extractor"
          :key="`${extractor}-${index}`"
        >
          <template v-slot:callToAction>
            <button @click="installExtractor(extractor)" class="card-button">Install</button>
          </template>
        </ConnectorCard>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-column-gap: 15px;
  grid-row-gap: 15px;
}

.installed-connectors {
  display: grid;
  grid-row-gap: 15px;
}

.card-button {
  width: 100%;
  background-color: hsl(210, 100%, 42%);
  color: #fff;
  text-align: center;
  padding: 10px 0;
  font-size: 1rem;
  transition: background 0.2s ease-in;
  cursor: pointer;

  &:hover {
    background-color: hsl(210, 74%, 22%);
  }
}

.connector-input {
  margin-top: 15px;
}
</style>
