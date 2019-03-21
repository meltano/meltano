<script>
import { mapState } from 'vuex';

export default {
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
  <article class="content">
    <h1 class="title is-2">Taps</h1>
    <input type="text" v-model="filterText">
    <h2 class="title is-3">Installed</h2>
    <ul>
      <li v-for="(extractor, index) in filteredInstalledPlugins" 
        :key="`${extractor.name}`"
      >
        {{ extractor.name }} <button @click="uninstallPlugin(index)">Uninstall</button>
      </li>
    </ul>
    <h2 class="title is-3">Available</h2>
    <ul>
      <li v-for="(extractor, index) in filteredExtractors" 
        :key="`${extractor}`"
      >
        {{ extractor }} <button @click="installPlugin(index)">Install</button>
      </li>
    </ul>
  </article>
</template>

<style>

</style>
