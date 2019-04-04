<script>
import BaseAccordion from '@/components/generic/BaseAccordion';
import BaseCard from '@/components/generic/BaseCard';

import { mapState } from 'vuex';

import orchestrationsApi from '../api/orchestrations';

export default {
  components: {
    BaseAccordion,
    BaseCard,
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
      'installedPlugins',
    ]),
    filteredExtractors() {
      if (this.filterText) {
        return this.extractors.filter(item => item.indexOf(this.filterText) > -1);
      }
      return this.extractors;
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
        <div>
          <BaseCard v-for="extractor in filteredInstalledPlugins"
            :key="`${extractor.name}`"
          >
            <div>
              <img :src="`/static/logos/${extractor.name.replace('tap-', '')}-logo.svg`" width="100" height="100" alt="" />
             {{ extractor.name }}
            </div>
          </BaseCard>
        </div>
        <h2 class="title is-4">Available</h2>
        <p v-if="installingPlugin">Installing...</p>
        <progress v-if="installingPlugin" class="progress is-small is-info" max="100">15%</progress>
        <!-- <p v-if="filteredExtractors.length === 0">All available extractors have been installed.</p> -->
        <div class="card-grid">
          <BaseCard v-for="(extractor, index) in filteredExtractors"
            :key="`${extractor}`"
          >
            <div style="display: flex; margin: 20px 0; align-items: center; flex: 1">
              <div style="display: flex; align-items: center;  margin-bottom: 0; justify-content: center; margin-top: 15px; margin-bottom: 10px; min-width: 150px; padding: 30px; box-sizing: border-box;">
                <img :src="`/static/logos/${extractor.replace('tap-', '')}-logo.png`" alt="" style="max-width: 150px; padding: 15px;" />
              </div>
              <div style="padding-top: 0;">
                <h3 style="margin-top: 0; margin-bottom: 10px;">{{ extractor }}</h3>
                <p style="font-size: 1rem;">This data source focuses on getting emissions data from local areas.</p>
                <p><a href="#">More information about Carbon Intensity tap</a></p>
              </div>
            </div>
            <div>
              <button @click="installPlugin(index, extractor)" style="width: 100%; background-color: blue; color: #fff; text-align: center; padding: 10px 0; font-size: 1rem;">Install</button>
            </div>
          </BaseCard>
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
        <ul>
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

.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-column-gap: 15px;
  grid-row-gap: 15px;
}
</style>
