<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
import _ from 'lodash'

import capitalize from '@/filters/capitalize'

export default {
  name: 'CreatePipelineScheduleModal',
  components: {},
  filters: {
    capitalize
  },
  data() {
    return {
      isLoaded: false,
      extractorInFocus: null,
      intervalOptions: {
        '@once': 'Once (Manual)',
        '@hourly': 'Hourly',
        '@daily': 'Daily',
        '@weekly': 'Weekly',
        '@monthly': 'Monthly',
        '@yearly': 'Yearly'
      },
      isSaving: false,
      isValidConfig: false,
      transformOptions: ['run', 'only', 'skip'],
      isTransformDisabled: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: 'target-postgres',
        transform: 'run',
        interval: '',
        isRunning: false
      }
    }
  },
  computed: {
    ...mapGetters('orchestration', [
      'getHasPipelineWithExtractor',
      'getHasValidConfigSettings',
      'getPipelineWithExtractor'
    ]),
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'visibleExtractors',
      'visibleLoaders',
      'getPluginLabel',
      'getHasDefaultTransforms'
    ]),
    ...mapState('orchestration', ['extractorInFocusConfiguration']),
    isSaveable() {
      const hasOwns = []
      _.forOwn(this.pipeline, val => hasOwns.push(val))
      const isValidPipeline =
        hasOwns.find(val => val === '' || val === null) === undefined
      const hasPipelineMatch = this.getHasPipelineWithExtractor(
        this.pipeline.extractor
      )
      return isValidPipeline && this.isValidConfig && !hasPipelineMatch
    }
  },
  watch: {
    extractorInFocusConfiguration: {
      handler() {
        this.checkConfiguration(this.pipeline.extractor)
      },
      deep: true
    }
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins').then(this.prepareForm)
  },
  methods: {
    ...mapActions('orchestration', [
      'getExtractorConfiguration',
      // 'run',
      'savePipelineSchedule'
    ]),
    checkConfiguration(extractorName) {
      this.isValidConfig = false
      if (!this.getIsPluginInstalled('extractors', extractorName)) {
        return
      }

      // let's lazy load the configuration here
      const uponConfig = _.isEmpty(this.extractorInFocusConfiguration)
        ? this.getExtractorConfiguration(extractorName)
        : Promise.resolve(this.extractorInFocusConfiguration)

      uponConfig.then(this.validateConfiguration)
    },
    onSelected(extractor) {
      this.extractorInFocus = extractor
      this.pipeline.extractor = this.extractorInFocus.name
      this.checkConfiguration(this.pipeline.extractor)
    },
    prepareForm() {
      this.pipeline.name = `pipeline-${new Date().getTime()}`
      this.pipeline.extractor = ''
      this.pipeline.isRunning = false
      this.isLoaded = true
    },
    onExtractorChange() {
      const extractor = this.visibleExtractors.find(
        el => el.name == this.pipeline.extractor
      )
      const hasDefaultTransforms = this.getHasDefaultTransforms(
        extractor.namespace
      )
      if (!hasDefaultTransforms) {
        this.pipeline.transform = 'skip'
        this.isTransformDisabled = true
      } else {
        this.pipeline.transform = 'run'
      }
    },
    save() {
      this.isSaving = true
      this.savePipelineSchedule({
        pipeline: this.pipeline
      })
        .then(() => {
          const savedPipeline = this.getPipelineWithExtractor(
            this.pipeline.extractor
          )
          Vue.toasted.global.success(`Schedule Saved - ${savedPipeline.name}`)
          // this.run(savedPipeline).then(() => {
          //   Vue.toasted.global.success(`Auto Running - ${savedPipeline.name}`)
          //   this.$router.push({
          //     name: 'runLog',
          //     params: { jobId: savedPipeline.jobId }
          //   })
          // })
        })
        .catch(error => {
          Vue.toasted.global.error(error.response.data.code)
        })
        .finally(() => {
          this.isSaving = false
          this.close()
        })
    },
    close() {
      this.$emit('close')
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <h3 class="modal-card-title">Create a pipeline</h3>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <progress
          v-if="!isLoaded || isSaving"
          class="progress is-small is-info"
        ></progress>
        <div v-else-if="isLoaded" class="columns is-multiline">
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 1</small>
            <h4>Data Sources</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select
                  v-model="pipeline.extractor"
                  class="select is-fullwidth"
                  @change="onExtractorChange($event)"
                >
                  <option value="">Select extractor</option>
                  <option
                    v-for="(extractor, index) in visibleExtractors"
                    :key="`${extractor.name}-${index}`"
                    :value="extractor.name"
                    >{{ getPluginLabel('extractors', extractor.name) }}
                  </option>
                </select>
              </span>
            </div>
            <router-link to="connections" class="has-text-underlined">
              Manage extractors
            </router-link>
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 2</small>
            <h4>Loader</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select v-model="pipeline.loader" class="select is-fullwidth">
                  <option value="">Select loader</option>
                  <option
                    v-for="(loader, index) in visibleLoaders"
                    :key="`${loader.name}-${index}`"
                    :value="loader.name"
                  >
                    {{ getPluginLabel('loaders', loader.name) }}
                  </option>
                </select>
              </span>
            </div>
            <!-- Uncomment when #2071 ready -->
            <!-- <router-link to="loaders" class="has-text-underlined">
              Manage loaders
            </router-link> -->
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 3</small>
            <h4>Transform</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select
                  v-model="pipeline.transform"
                  :disabled="isTransformDisabled"
                >
                  <option value="">Select transform type</option>
                  <option
                    v-for="(transform, index) in transformOptions"
                    :key="`${transform}-${index}`"
                    :value="transform"
                  >
                    {{ transform | capitalize }}
                  </option>
                </select>
              </span>
            </div>
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 3</small>
            <h4>Interval</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select v-model="pipeline.interval">
                  <option value="">Select interval</option>
                  <option
                    v-for="(interval, label) in intervalOptions"
                    :key="label"
                    :value="label"
                    >{{ interval }}</option
                  >
                </select>
              </span>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="isSaving"
          @click="save"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.control {
  margin: 0.5rem 0;
}
</style>
