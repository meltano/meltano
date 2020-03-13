<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import ExtractorList from '@/components/pipelines/ExtractorList'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Connections',
  components: {
    ExtractorList,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('plugins', ['getIsLoadingPluginsOfType']),
    ...mapState('plugins', ['installedPlugins']),
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
  },
  created() {
    this.getPipelineSchedules()
    this.getPlugins()
    // Until we want to reintroduce a "Loader" UI, we will default to loading target-postgres as the default loader
    this.getInstalledPlugins().then(this.tryInstallLoaderPostgres)
  },
  methods: {
    ...mapActions('orchestration', ['getPipelineSchedules']),
    ...mapActions('plugins', [
      'addPlugin',
      'getPlugins',
      'getInstalledPlugins',
      'installPlugin'
    ]),
    tryInstallLoaderPostgres() {
      const loaderPostgres = 'target-postgres'
      const isInstalled =
        this.installedPlugins.loaders &&
        this.installedPlugins.loaders.find(
          plugin => plugin.name === loaderPostgres
        )
      if (!isInstalled) {
        const config = {
          pluginType: 'loaders',
          name: loaderPostgres
        }
        this.addPlugin(config).then(() => {
          this.installPlugin(config)
        })
      }
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <h2 id="data" class="title">Connections</h2>

      <div class="columns">
        <div class="column">
          <div class="box">
            <progress
              v-if="getIsLoadingPluginsOfType('extractors')"
              class="progress is-small is-info"
            ></progress>
            <ExtractorList v-else />
          </div>
        </div>
      </div>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
