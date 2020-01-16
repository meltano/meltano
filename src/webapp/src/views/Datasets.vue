<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import CreatePipelineSchedule from '@/components/pipelines/CreatePipelineSchedule'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Datasets',
  components: {
    CreatePipelineSchedule,
    PipelineSchedules,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('orchestration', ['getHasPipelines']),
    ...mapState('plugins', ['installedPlugins']),
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
  },
  created() {
    this.getAllPipelineSchedules()
    this.getAllPlugins()
    // Until we want to reintroduce a "Loader" UI, we will default to loading target-postgres as the default loader
    this.getInstalledPlugins().then(this.tryInstallLoaderPostgres)
  },
  methods: {
    ...mapActions('orchestration', ['getAllPipelineSchedules']),
    ...mapActions('plugins', [
      'addPlugin',
      'getAllPlugins',
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
    <div class="container view-body is-fluid">
      <h2 id="data" class="title">Data</h2>
      <p class="subtitle">Integrations and custom data connections</p>

      <div class="columns">
        <div class="column">
          <CreatePipelineSchedule />
        </div>
      </div>

      <template v-if="getHasPipelines" class="columns">
        <br />
        <div class="columns">
          <div class="column">
            <div class="content">
              <h3 id="pipelines" class="title">Pipelines</h3>
              <p class="subtitle">Scheduled data collection</p>
            </div>
            <PipelineSchedules />
          </div>
        </div>
      </template>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
