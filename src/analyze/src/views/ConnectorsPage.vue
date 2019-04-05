<script>
import BaseAccordion from '@/components/generic/BaseAccordion';
import ExtractorEntities from '@/components/orchestration/ExtractorEntities';

import { mapState } from 'vuex';

import orchestrationsApi from '../api/orchestrations';

export default {
  components: {
    BaseAccordion,
    ExtractorEntities,
  },
  data() {
    return {
      filterText: '',
      installingPlugin: false,
    };
  },
  computed: {
    ...mapState('orchestrations', [
      'extractors',
      'extractorEntities',
      'installedPlugins',
    ]),
    filteredExtractors() {
      if (this.filterText) {
        return this.extractors.filter(item => item.indexOf(this.filterText) > -1);
      }
      return this.extractors;
    },
    filteredInstalledPlugins() {
      if (this.installedPlugins.extractors) {
        if (this.filterText) {
          return this.installedPlugins.extractors.filter(
            item => item.name.indexOf(this.filterText) > -1,
          );
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
        <p v-if="!filteredInstalledPlugins || filteredInstalledPlugins.length < 1">
          No extractors currently installed
        </p>
        <ul v-else>
          <li v-for="extractor in filteredInstalledPlugins"
            :key="`${extractor.name}`"
          >
            {{ extractor.name }}
          </li>
        </ul>
        <h2 class="title is-4">Available</h2>
        <p v-if="installingPlugin">Installing...</p>
        <progress v-if="installingPlugin" class="progress is-small is-info" max="100">15%</progress>
        <p v-if="filteredExtractors.length === 0">All available extractors have been installed.</p>
        <ul v-else>
          <li v-for="(extractor, index) in filteredExtractors"
            :key="`${extractor}`"
          >
            {{ extractor }} <button @click="installPlugin(index, extractor)">Install</button>
          </li>
        </ul>

        <ExtractorEntities :extractor-entities='extractorEntities'></ExtractorEntities>

      </template>
    </base-accordion>
    <base-accordion>
      <template slot="header">
        <h2 class="title is-3 has-text-white is-marginless">Loaders</h2>
      </template>
      <template slot="body">
        <input type="text" v-model="filterText" placeholder="Filter loaders..." class="input">
        <h2 class="title is-4">Installed</h2>
        <p v-if="filteredInstalledPlugins.length === 0">No loaders currently installed</p>
        <ul v-else>
          <li v-for="(extractor, index) in filteredInstalledPlugins"
            :key="`${extractor.name}`"
          >
            {{ extractor.name }}
            <button @click="uninstallPlugin(index)">Uninstall</button>
            <button>Configure</button>
            <div>
              <label for="Database"></label>
              <input type="text">
            </div>
          </li>
        </ul>
        <h2 class="title is-4">Available</h2>
        <p v-if="filteredExtractors.length === 0">All available loaders have been installed.</p>
        <ul v-else>
          <li v-for="(extractor, index) in filteredExtractors"
            :key="`${extractor}`"
          >
            {{ extractor }} <button @click="installPlugin(index)">Install</button>
          </li>
        </ul>
      </template>
    </base-accordion>
  </div>
</template>

<style lang="scss">
.content {
  padding: 20px;
}
</style>
