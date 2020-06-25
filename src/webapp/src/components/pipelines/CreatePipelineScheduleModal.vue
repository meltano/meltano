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
      isSaving: false,
      isValidConfig: false,
      transformOptions: ['run', 'only', 'skip'],
      hasDefaultTransforms: true,
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: 'run',
        interval: '',
        isRunning: false
      }
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'getPluginLabel',
      'getHasDefaultTransforms'
    ]),
    ...mapState('plugins', ['installedPlugins']),
    ...mapState('orchestration', ['intervalOptions']),
    isSaveable() {
      const hasOwns = []
      _.forOwn(this.pipeline, val => hasOwns.push(val))
      const isValidPipeline =
        hasOwns.find(val => val === '' || val === null) === undefined
        
      const isTransformValid =
        this.hasDefaultTransforms || this.pipeline.transform === 'skip'
      return isValidPipeline && isTransformValid
    }
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins').then(this.prepareForm)
  },
  methods: {
    ...mapActions('orchestration', ['savePipelineSchedule']),
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
      const extractor = this.installedPlugins.extractors.find(
        el => el.name == this.pipeline.extractor
      )
      this.hasDefaultTransforms = this.getHasDefaultTransforms(
        extractor.namespace
      )
      if (!this.hasDefaultTransforms) {
        this.pipeline.transform = 'skip'
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
          Vue.toasted.global.success(`Pipeline Saved - ${this.pipeline.name}`)
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
                  @change="onExtractorChange($event)"
                >
                  <option value="">Select extractor</option>
                  <option
                    v-for="(extractor, index) in installedPlugins.extractors"
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
                    v-for="(loader, index) in installedPlugins.loaders"
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
          <div class="column is-full">
            <p 
              v-if="!hasDefaultTransforms && pipeline.transform !== 'skip'"
              class="has-text-grey"
            >
              Your Meltano project does not contain a transform plugin for this extractor. Only proceed with running transformations as part of your pipeline if you've added these manually.
            </p>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
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
</style>
