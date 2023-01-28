<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import PipelineSchedules from '@/components/pipelines/PipelineSchedules'

import RouterViewLayout from '@/views/RouterViewLayout'

import _ from 'lodash'

export default {
  name: 'Pipelines',
  components: {
    PipelineSchedules,
    RouterViewLayout,
  },
  data() {
    return {
      isLoading: true,
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getHasPipelines', 'getSortedPipelines']),
    ...mapGetters('plugins', ['getInstalledPlugin']),
    ...mapState('plugins', ['installedPlugins']),
    getModalName() {
      return this.$route.name
    },
    hasExtractors() {
      return (
        this.installedPlugins.extractors &&
        this.installedPlugins.extractors.length
      )
    },
    hasLoaders() {
      return (
        this.installedPlugins.loaders && this.installedPlugins.loaders.length
      )
    },
    isModal() {
      return this.$route.meta.isModal
    },
    cloneDeepPipelines() {
      return _.cloneDeep(this.getSortedPipelines).map((pipeline) => {
        if (!pipeline.interval) {
          pipeline.interval = '@once'
          return pipeline
        } else if (pipeline.interval.includes('*')) {
          pipeline.cronExpression = pipeline.interval
          pipeline.interval = '@other'
          return pipeline
        } else {
          return pipeline
        }
      })
    },
  },
  created() {
    Promise.all([this.getPipelineSchedules(), this.getInstalledPlugins()]).then(
      () => {
        this.isLoading = false
      }
    )
  },
  methods: {
    ...mapActions('orchestration', [
      'getPipelineSchedules',
      'updatePipelineSchedule',
    ]),
    ...mapActions('plugins', ['getInstalledPlugins']),
  },
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <div class="columns">
        <div class="column">
          <h2 id="data" class="title">Pipelines</h2>
        </div>
        <div class="column is-one-quarter has-text-right">
          <router-link
            :to="{
              name: 'createPipelineSchedule',
            }"
            class="button is-interactive-primary"
          >
            Create
          </router-link>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div v-if="isLoading" class="box">
            <progress class="progress is-small is-info"></progress>
          </div>
          <div v-else>
            <PipelineSchedules
              v-if="getHasPipelines"
              :pipelines="cloneDeepPipelines"
            />
            <div v-else class="box">
              <p>
                No pipelines have been set up yet.
                <router-link
                  v-if="hasExtractors && hasLoaders"
                  :to="{
                    name: 'createPipelineSchedule',
                  }"
                >
                  Create one now
                </router-link>
                <span v-else>
                  Add
                  <span v-if="!hasExtractors">
                    an
                    <router-link to="extractors">extractor</router-link>
                  </span>
                  <span v-if="!hasLoaders">
                    <span v-if="!hasExtractors"> and </span>
                    a
                    <router-link to="loaders">loader</router-link>
                  </span>
                  first.
                </span>
              </p>
            </div>
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
