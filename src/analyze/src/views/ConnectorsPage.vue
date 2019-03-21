<script>
import { mapState } from 'vuex';

import BaseAccordion from '@/components/generic/BaseAccordion.vue';

export default {
  components: {
    BaseAccordion
  },
  data () {
    return {
      filterText: '',
      tempInstalledPlugins: {
        extractors: [
          {
            name: 'tap-carbon-intensity'
          }
        ]
      },
      tempExtractors: [
        "tap-gitlab",
        "tap-zendesk",
        "tap-zuora",
        "tap-marketo",
        "tap-salesforce",
        "tap-mongodb",
        "tap-stripe",
        "tap-fastly",
      ]
    }
  },
  computed: {
    ...mapState('orchestrations', [
      'extractors',
      'installedPlugins'
    ]),
    filteredExtractors() {
      if (this.filterText) {
        return this.tempExtractors.filter((item) => item.indexOf(this.filterText) > -1)
      } else {
        return this.tempExtractors
      }
    },
    filteredInstalledPlugins() {
      if (this.filterText) {
        return this.tempInstalledPlugins.extractors.filter((item) => item.name.indexOf(this.filterText) > -1)
      } else {
        return this.tempInstalledPlugins.extractors
      }
    }
  },
  methods: {
    installPlugin(index) {
      const plugin = this.tempExtractors.splice(index, 1)

      this.tempInstalledPlugins.extractors.push({
        name: plugin[0]
      })
    },
    uninstallPlugin(index) {
      const extractor = this.tempInstalledPlugins.extractors.splice(index, 1)

      this.tempExtractors.push(extractor[0].name)
    }
  },
  created () {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  }
};
</script>

<template>
  <div class="content">
    <h1 class="title is-2">Connectors</h1>
    <base-accordion>
      <template slot="header">
        <h2 class="title is-3 has-text-white is-marginless">Extractors</h2>
      </template>
      <template slot="body">
        <input type="text" v-model="filterText" placeholder="Filter extractors..." class="input">
        <h2 class="title is-4">Installed</h2>
        <p v-if="filteredInstalledPlugins.length === 0">No extractors currently installed</p>
        <ul v-else>
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
        <p v-if="filteredExtractors.length === 0">All available extractors have been installed.</p>
        <ul v-else>
          <li v-for="(extractor, index) in filteredExtractors" 
            :key="`${extractor}`"
          >
            {{ extractor }} <button @click="installPlugin(index)">Install</button>
          </li>
        </ul>
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
            {{ extractor.name }} <button @click="uninstallPlugin(index)">Uninstall</button> <button>Configure</button>
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
