<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import ExtractorList from '@/components/pipelines/ExtractorList'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Datasets',
  components: {
    ExtractorList,
    PipelineSchedules,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('orchestration', ['getHasPipelines', 'getSortedPipelines']),
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
      <h2 id="data" class="title">Data</h2>

      <template v-if="getHasPipelines" class="columns">
        <div class="columns">
          <div class="column">
            <div class="content">
              <h3 id="pipelines" class="title">Pipelines</h3>
              <p class="subtitle">Scheduled data collection</p>
            </div>
            <PipelineSchedules :pipelines="getSortedPipelines" />
          </div>
        </div>
      </template>

      <div class="columns">
        <div class="column">
          <div class="content">
            <h3 id="integrations" class="title">Integrations</h3>
            <p class="subtitle">Integrations and custom data connections</p>
          </div>
          <div class="box">
            <progress
              v-if="getIsLoadingPluginsOfType('extractors')"
              class="progress is-small is-info"
            ></progress>
            <template v-else>
              <ExtractorList />
              <hr />
              <article class="media">
                <figure class="media-left">
                  <p class="image level-item container">
                    <span class="icon is-large fa-2x has-text-grey-light">
                      <font-awesome-icon icon="plus"></font-awesome-icon>
                    </span>
                  </p>
                </figure>
                <div class="media-content">
                  <div class="content">
                    <p>
                      <span class="has-text-weight-bold">Custom</span>
                      <br />
                      <small>Connect a data source not listed above</small>
                    </p>
                  </div>
                </div>
                <figure class="media-right is-flex is-flex-column is-vcentered">
                  <a
                    href="https://www.meltano.com/tutorials/create-a-custom-extractor.html"
                    target="_blank"
                    class="button is-text tooltip is-tooltip-left"
                    data-tooltip="Create your own data source"
                  >
                    <span>Learn More</span>
                  </a>
                </figure>
              </article>
            </template>
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
