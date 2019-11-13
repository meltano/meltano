<script>
import { mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'

import _ from 'lodash'

export default {
  name: 'CreateScheduleModal',
  components: {
    ScheduleTableHead
  },
  data() {
    return {
      intervalOptions: [
        '@once',
        '@hourly',
        '@daily',
        '@weekly',
        '@monthly',
        '@yearly'
      ],
      isSaving: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: '',
        interval: '',
        isRunning: false
      }
    }
  },
  computed: {
    ...mapState('configuration', ['recentELTSelections', 'transformOptions']),
    ...mapGetters('plugins', ['getHasInstalledPluginsOfType']),
    ...mapState('plugins', ['installedPlugins']),
    isSaveable() {
      const hasOwns = []
      _.forOwn(this.pipeline, val => hasOwns.push(val))
      return hasOwns.find(val => val === '' || val === null) === undefined
    }
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins').then(this.prefillForm)
  },
  mounted() {
    this.$refs.name.focus()
  },
  methods: {
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'schedules' })
      }
    },
    prefillForm() {
      // TODO implement an intelligent prefill approach
      this.pipeline.name = `pipeline-${new Date().getTime()}`

      const defaultExtractor =
        this.recentELTSelections.extractor ||
        (!_.isEmpty(this.installedPlugins.extractors) &&
          this.installedPlugins.extractors[0])
      this.pipeline.extractor = defaultExtractor ? defaultExtractor.name : ''

      const defaultLoader =
        this.recentELTSelections.loader ||
        (!_.isEmpty(this.installedPlugins.loaders) &&
          this.installedPlugins.loaders[0])
      this.pipeline.loader = defaultLoader ? defaultLoader.name : ''

      const defaultTransform =
        this.recentELTSelections.transform ||
        (!_.isEmpty(this.transformOptions) && this.transformOptions[0])
      this.pipeline.transform = defaultTransform ? defaultTransform.name : ''

      this.pipeline.interval = !_.isEmpty(this.intervalOptions)
        ? this.intervalOptions[0]
        : ''
    },
    save() {
      this.isSaving = true
      this.$store
        .dispatch('configuration/savePipelineSchedule', this.pipeline)
        .then(() => {
          this.$store.dispatch('configuration/run', this.pipeline).then(() => {
            Vue.toasted.global.success(`Schedule Saved - ${this.pipeline.name}`)
            Vue.toasted.global.success(`Auto Running - ${this.pipeline.name}`)
            this.isSaving = false
            this.$router.push({
              name: 'runLog',
              params: { jobId: this.pipeline.jobId }
            })
          })
        })
        .catch(error => {
          this.isSaving = false
          Vue.toasted.global.error(error.response.data.code)
        })
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">Create Pipeline</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <table class="table is-fullwidth">
          <ScheduleTableHead />

          <tbody>
            <tr>
              <td>
                <div class="control is-expanded">
                  <input
                    ref="name"
                    v-model="pipeline.name"
                    class="input"
                    :class="{
                      'has-text-success': pipeline.name
                    }"
                    type="text"
                    placeholder="Name"
                    @focus="$event.target.select()"
                  />
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{ 'is-loading': !pipeline.extractor }"
                  >
                    <select
                      v-model="pipeline.extractor"
                      :class="{ 'has-text-success': pipeline.extractor }"
                      :disabled="!getHasInstalledPluginsOfType('extractors')"
                    >
                      <option
                        v-for="extractor in installedPlugins.extractors"
                        :key="extractor.name"
                        >{{ extractor.name }}</option
                      >
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{ 'is-loading': !pipeline.loader }"
                  >
                    <select
                      v-model="pipeline.loader"
                      :class="{ 'has-text-success': pipeline.loader }"
                      :disabled="!getHasInstalledPluginsOfType('loaders')"
                    >
                      <option
                        v-for="loader in installedPlugins.loaders"
                        :key="loader.name"
                        >{{ loader.name }}</option
                      >
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control">
                  <span
                    class="select is-fullwidth"
                    :class="{ 'is-loading': !pipeline.transform }"
                  >
                    <select
                      v-model="pipeline.transform"
                      :class="{ 'has-text-success': pipeline.transform }"
                    >
                      <option
                        v-for="transform in transformOptions"
                        :key="transform.name"
                        >{{ transform.name }}</option
                      >
                    </select>
                  </span>
                </div>
              </td>
              <td>
                <div class="control is-expanded">
                  <span
                    class="select is-fullwidth"
                    :class="{ 'is-loading': !pipeline.interval }"
                  >
                    <select
                      v-model="pipeline.interval"
                      :class="{ 'has-text-success': pipeline.interval }"
                    >
                      <option
                        v-for="interval in intervalOptions"
                        :key="interval"
                        >{{ interval }}</option
                      >
                    </select>
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :class="{ 'is-loading': isSaving }"
          :disabled="!isSaveable"
          @click="save"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
