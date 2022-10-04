<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'
import _ from 'lodash'

import { PIPELINE_INTERVAL_OPTIONS, TRANSFORM_OPTIONS } from '@/utils/constants'
import capitalize from '@/filters/capitalize'
import VueCronEditorBuefy from 'vue-cron-editor-buefy'

export default {
  name: 'CreatePipelineScheduleModal',
  filters: {
    capitalize,
  },
  components: {
    VueCronEditorBuefy,
  },
  data() {
    return {
      isLoaded: false,
      isSaving: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: 'skip',
        interval: '',
        isRunning: false,
      },
      cronExpression: '*/1 * * * *',
    }
  },
  computed: {
    ...mapGetters('plugins', ['getPluginLabel', 'getHasDefaultTransforms']),
    ...mapState('plugins', ['installedPlugins']),
    transformOptions() {
      return TRANSFORM_OPTIONS
    },
    intervalOptions() {
      return PIPELINE_INTERVAL_OPTIONS
    },
    isSaveable() {
      const hasOwns = []
      _.forOwn(this.pipeline, (val) => hasOwns.push(val))
      const isValidPipeline =
        hasOwns.find((val) => val === '' || val === null) === undefined

      return isValidPipeline
    },
    hasDefaultTransforms() {
      const pipelineExtractor = this.pipeline.extractor
      if (!pipelineExtractor) {
        return true
      }
      const extractor = this.installedPlugins.extractors.find(
        (plugin) => plugin.name === pipelineExtractor
      )
      return this.getHasDefaultTransforms(extractor.namespace)
    },
    showTransformWarning() {
      return (
        !this.hasDefaultTransforms &&
        (this.pipeline.transform === 'run' ||
          this.pipeline.transform === 'only')
      )
    },
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
      this.isLoaded = true

      const { extractor, loader } = this.$route.query
      if (extractor) {
        this.pipeline.extractor = extractor
      }
      if (loader) {
        this.pipeline.loader = loader
      }
    })
  },
  methods: {
    ...mapActions('orchestration', [
      'savePipelineSchedule',
      'getPipelineSchedules',
    ]),
    onExtractorLoaderChange() {
      if (!this.pipeline.extractor || !this.pipeline.loader) {
        return
      }

      this.pipeline.name =
        this.pipeline.extractor.replace(/^tap-/, '') +
        '-to-' +
        this.pipeline.loader.replace(/^target-/, '')
    },
    save() {
      this.isSaving = true
      if (this.pipeline.interval === '@other') {
        this.pipeline.interval = this.cronExpression
      }
      this.savePipelineSchedule({
        pipeline: this.pipeline,
      })
        .then(() => {
          this.getPipelineSchedules()
        })
        .then(() => {
          Vue.toasted.global.success(`Pipeline Saved - ${this.pipeline.name}`)
          this.close()
        })
        .catch((error) => {
          Vue.toasted.global.error(error.response.data.code)
        })
        .finally(() => {
          this.isSaving = false
        })
    },
    close() {
      this.$router.push({ name: 'pipelines' })
    },
  },
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
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
            <h4>Extractor</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select
                  v-model="pipeline.extractor"
                  class="select is-fullwidth"
                  @change="onExtractorLoaderChange"
                >
                  <option value="">Select extractor</option>
                  <option
                    v-for="(extractor, index) in installedPlugins.extractors"
                    :key="`${extractor.name}-${index}`"
                    :value="extractor.name"
                  >
                    {{ getPluginLabel('extractors', extractor.name) }}
                  </option>
                </select>
              </span>
            </div>
            <router-link
              :to="{ name: 'extractors' }"
              class="has-text-underlined"
            >
              Manage extractors
            </router-link>
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 2</small>
            <h4>Loader</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select
                  v-model="pipeline.loader"
                  class="select is-fullwidth"
                  @change="onExtractorLoaderChange"
                >
                  <option value="">Select loader</option>
                  <option
                    v-for="(loader, index) in installedPlugins.loaders"
                    :key="`${loader.name}-${index}`"
                    :value="loader.name"
                  >
                    {{ getPluginLabel('loaders', loader.name) }}
                  </option>
                </select>
              </span>
            </div>
            <router-link :to="{ name: 'loaders' }" class="has-text-underlined">
              Manage loaders
            </router-link>
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 3</small>
            <h4>Transform</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select v-model="pipeline.transform">
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
            <small class="has-text-interactive-navigation">Step 4</small>
            <h4>Interval</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <select v-model="pipeline.interval">
                  <option value="">Select interval</option>
                  <option
                    v-for="(interval, label) in intervalOptions"
                    :key="label"
                    :value="label"
                  >
                    {{ interval }}
                  </option>
                </select>
              </span>
            </div>
          </div>
          <div class="column is-half">
            <small class="has-text-interactive-navigation">Step 5</small>
            <h4>Name</h4>
            <div class="control is-expanded">
              <input
                v-model="pipeline.name"
                class="input is-fullwidth"
                type="text"
              />
            </div>
          </div>
          <div
            v-if="pipeline.interval === '@other'"
            class="column is-fullwidth"
          >
            <small class="has-text-interactive-navigation">Step 4a</small>
            <h4 class="current-cron-expression">
              This is your current CRON expression
              <code>{{ cronExpression }}</code
              >.
            </h4>
            <VueCronEditorBuefy v-model="cronExpression" />
          </div>
          <div class="column is-full">
            <p v-if="showTransformWarning" class="has-text-grey">
              Your Meltano project does not contain a transform plugin for this
              extractor. Only proceed with running transformations as part of
              your pipeline if you've added these manually.
            </p>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <router-link class="button" :to="{ name: 'pipelines' }"
          >Cancel</router-link
        >
        <button
          class="button is-interactive-primary"
          :disabled="isSaving || !isSaveable"
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

.columns .is-fullwidth {
  padding-right: 0;
}

.current-cron-expression {
  margin-bottom: 10px;
}
</style>
