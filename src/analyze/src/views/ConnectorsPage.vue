<script>
import BaseAccordion from '@/components/generic/BaseAccordion';
import BaseCard from '@/components/generic/BaseCard';
import ConnectorCard from '@/components/ConnectorCard';

import { mapState, mapGetters } from 'vuex';

import orchestrationsApi from '../api/orchestrations';

export default {
  components: {
    BaseAccordion,
    BaseCard,
    ConnectorCard
  },
  data() {
    return {
      filterText: '',
      installingPlugin: false,
    };
  },
  computed: {
    ...mapState('orchestrations', [
      'loaders',
      'installedPlugins',
    ]),
    ...mapGetters('orchestrations', [
      'remainingExtractors'
    ]),
    filteredExtractors() {
      if (this.filterText) {
        return this.remainingExtractors.filter(item => item.indexOf(this.filterText) > -1);
      }
      return this.remainingExtractors;
    },
    filteredInstalledPlugins() {
      if (this.installedPlugins) {
        if (this.filterText) {
          return this.installedPlugins.extractors.filter(item => item.name.indexOf(this.filterText) > -1);
        }
        return this.installedPlugins.extractors;
      }
      return [];
    },
    filteredLoaders() {
      if (this.filterText) {
        return this.loaders.filter(item => item.indexOf(this.filterText) > -1);
      }
      return this.loaders;
    },
    filteredInstalledLoaders() {
      if (this.installedPlugins) {
        if (this.filterText) {
          return this.installedPlugins.extractors.filter(item => item.name.indexOf(this.filterText) > -1);
        }
        return this.installedPlugins.extractors;
      }
      return [];
    },
  },
  methods: {
    installPlugin(index, extractor) {
      this.installingPlugin = true;

      orchestrationsApi.addExtractors({
        name: extractor,
      }).then((response) => {
        if (response.status === 200) {
          this.$store.dispatch('orchestrations/updateExtractors', index);
          this.$store.dispatch('orchestrations/getInstalledPlugins')
            .then(() => {
              this.installingPlugin = false;
            });
        }
      });
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
        <input type="text" v-model="filterText" placeholder="Filter extractors..." class="input">
        <h2 class="title is-4">Installed</h2>
        <!-- <p v-if="!filteredInstalledPlugins || filteredInstalledPlugins.length < 1">No extractors currently installed</p> -->
        <div class="installed-connectors">
          <ConnectorCard v-for="extractor in filteredInstalledPlugins"
            :connector="extractor.name"
            :key="`${extractor.name}`"
          >
          </ConnectorCard>
        </div>
        <h2 class="title is-4">Available</h2>
        <p v-if="installingPlugin">Installing...</p>
        <progress v-if="installingPlugin" class="progress is-small is-info" max="100">15%</progress>
        <p v-if="filteredExtractors.length === 0">All available extractors have been installed.</p>
        <div v-else class="card-grid">
          <ConnectorCard v-for="(extractor, index) in filteredExtractors"filteredExtractors
            :connector="extractor" 
            :key="`${extractor}-${index}`"
          >
            <template v-slot:callToAction>
              <button @click="installPlugin(index, extractor)" style="width: 100%; background-color: blue; color: #fff; text-align: center; padding: 10px 0; font-size: 1rem;">Install</button>
            </template>
          </ConnectorCard>
        </div>
      </template>
    </base-accordion>
    <base-accordion>
      <template slot="header">
        <h2 class="title is-3 has-text-white is-marginless">Loaders</h2>
      </template>
      <template slot="body">
        <input type="text" v-model="filterText" placeholder="Filter loaders..." class="input">
        <h2 class="title is-4">Installed</h2>
        <!-- <p v-if="filteredInstalledPlugins.length === 0">No loaders currently installed</p> -->
        <ul>
          <li v-for="(extractor, index) in filteredInstalledPlugins"
            :key="`${extractor.name}`"
          >
            {{ extractor.name }} <button @click="uninstallPlugin(index)">Uninstall</button> <button>Configure</button>
            <div>
              <label for="Database"></label>
              <input type="text">
            </div>
          </li>
        </ul>
        <h2 class="title is-4">Available</h2>
        <!-- <p v-if="filteredExtractors.length === 0">All available loaders have been installed.</p> -->
        <div class="card-grid">
          <ConnectorCard v-for="(loader, index) in filteredLoaders"
            :connector="loader" 
            :key="`${loader}-${index}`"
          >
            <template v-slot:callToAction>
              <button @click="installPlugin(index, loader)" style="width: 100%; background-color: blue; color: #fff; text-align: center; padding: 10px 0; font-size: 1rem;">Install</button>
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
</style>
