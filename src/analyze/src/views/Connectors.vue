<script>
import BaseAccordion from '@/components/generic/BaseAccordion';
import BaseCard from '@/components/generic/BaseCard';
import ConnectorCard from '@/components/orchestration/ConnectorCard';
import ConnectorSettings from '@/components/orchestration/ConnectorSettings';
import ExtractorEntities from '@/components/orchestration/ExtractorEntities';

import { mapState, mapGetters } from 'vuex';

import orchestrationsApi from '../api/orchestrations';

export default {
  name: 'Connectors',
  components: {
    BaseAccordion,
    BaseCard,
    ConnectorCard,
    ConnectorSettings,
    ExtractorEntities,
  },
  data() {
    return {
      filterExtractorsText: '',
      filterLoadersText: '',
      installingExtractor: false,
      installingLoader: false,
      extractorInFocus: null,
    };
  },
  computed: {
    ...mapState('orchestrations', [
      'installedPlugins',
      'extractors',
      'extractorEntities',
      'extractorSettings',
      'installedPlugins',
    ]),
    ...mapGetters('orchestrations', [
      'remainingExtractors',
      'remainingLoaders',
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
    filteredInstalledLoaders() {
      if (this.installedPlugins && this.installedPlugins.loaders) {
        if (this.filterLoadersText) {
          return this.installedPlugins.loaders
            .filter(item => item.name.indexOf(this.filterLoadersText) > -1);
        }
        return this.installedPlugins.loaders;
      }
      return [];
    },
    filteredLoaders() {
      if (this.filterLoadersText) {
        return this.remainingLoaders.filter(item => item.indexOf(this.filterLoadersText) > -1);
      }
      return this.remainingLoaders;
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
    installLoader(loader) {
      this.installingLoader = true;

      orchestrationsApi.addLoaders({
        name: loader,
      }).then((response) => {
        if (response.status === 200) {
          this.$store.dispatch('orchestrations/getInstalledPlugins')
            .then(() => {
              this.installingLoader = false;
            });
        }
      });
    },
    updateExtractorInFocus(extractor) {
      this.extractorInFocus = extractor;
    },
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
};
</script>

<template>
  <div class="content">
    <h1 class="title is-2">Connectors</h1>
    <base-accordion :isOpen="true">

      <template slot="header">
        <h2 class="title is-3 has-text-white is-marginless">Extractors</h2>
      </template>

      <template slot="body">

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

          <hr>

          <ExtractorEntities
            :extractor='extractorInFocus'
            :extractor-entities='extractorEntities'></ExtractorEntities>

        </div>

        <div v-else>
          <input
            type="text"
            v-model="filterExtractorsText"
            placeholder="Filter extractors..."
            class="input connector-input">
          <h2 class="title is-3">Installed</h2>
          <article class="message is-warning">
            <div class="message-header">
              <p>Warning</p>
            </div>
            <div class="message-body">
              <p>Extractor authentication settings are not currently supported in the UI. This work is in progress however.</p>
            </div>
          </article>
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
      </template>

    </base-accordion>
    <base-accordion :isOpen="true">

      <template slot="header">
        <h2 class="title is-3 has-text-white is-marginless">Loaders</h2>
      </template>
      <template slot="body">
        <input
          type="text"
          v-model="filterLoadersText"
          placeholder="Filter loaders..."
          class="input connector-input">
        <h2 class="title is-3">Installed</h2>
        <p v-if="filteredInstalledLoaders.length === 0">No loaders currently installed</p>
        <div v-else class="installed-connectors">
          <ConnectorCard v-for="(loader, index) in filteredInstalledLoaders"
            :connector="loader.name"
            :key="`${loader.name}-${index}`"
          >
          </ConnectorCard>
        </div>
        <h2 class="title is-3">Available</h2>
        <p v-if="installingLoader">Installing...</p>
        <progress v-if="installingLoader" class="progress is-small is-info"></progress>
        <p v-if="filteredExtractors.length === 0">All available loaders have been installed.</p>
        <div v-else class="card-grid">
          <ConnectorCard v-for="(loader, index) in filteredLoaders"
            :connector="loader"
            :key="`${loader}-${index}`"
          >
            <template v-slot:callToAction>
              <button @click="installLoader(loader)" class="card-button">Install</button>
            </template>
          </ConnectorCard>
        </div>
      </template>

    </base-accordion>
  </div>
</template>

<style lang="scss">
.content {
  padding: 20px;
}

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
