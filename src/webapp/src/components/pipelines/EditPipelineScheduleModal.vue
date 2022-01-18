<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import { PIPELINE_INTERVAL_OPTIONS, TRANSFORM_OPTIONS } from '@/utils/constants'
import capitalize from '@/filters/capitalize'

export default {
  name: 'EditPipelineScheduleModal',
  filters: {
    capitalize
  },
  data() {
    return {
      isLoaded: false,
      isSaving: false,
      updatedPipeline: {}
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'getPluginLabel',
      'getHasDefaultTransforms',
      'getInstalledPlugin'
    ]),
    ...mapState('orchestration', ['pipeline', 'pipelines']),
    ...mapState('plugins', ['installedPlugins']),
    transformOptions() {
      return TRANSFORM_OPTIONS
    },
    intervalOptions() {
      return PIPELINE_INTERVAL_OPTIONS
    },
    hasDefaultTransforms() {
      const pipelineExtractor = this.pipeline.extractor
      if (!pipelineExtractor) {
        return true
      }
      const extractor = this.installedPlugins.extractors.find(
        plugin => plugin.name === pipelineExtractor
      )
      return this.getHasDefaultTransforms(extractor.namespace)
    },
    showTransformWarning() {
      return (
        !this.hasDefaultTransforms &&
        (this.pipeline.transform === 'run' ||
          this.pipeline.transform === 'only')
      )
    }
  },
  async created() {
    await this.$store.dispatch(
      'orchestration/getPipelineByJobId',
      this.$route.params.jobId
    ),
      await this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
        this.isLoaded = true

        const { extractor, loader } = this.$route.query
        if (extractor) {
          this.pipeline.extractor = extractor
        }
        if (loader) {
          this.pipeline.loader = loader
        }
        // let clonedObject = Object.assign({}, obj)
        // let clonedThing = {...thing}
        // let clonedObject = Object.assign({}, obj)
      })
  },
  methods: {
    ...mapActions('orchestration', [
      'deletePipelineSchedule',
      'savePipelineSchedule',
      'updatePipelineDetails',
      'updatePipelineSchedule'
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
    inputUpdate(keyItem, update) {
      let valueItem
      if (update.srcElement.localName === 'select') {
        valueItem = update.srcElement.selectedOptions[0].value
      } else if (update.srcElement.localName === 'input') {
        valueItem = update.srcElement.value
      }
      this.$set(this.updatedPipeline, keyItem, valueItem)
    },
    kebabCase(str) {
      return str
        .match(
          /[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g
        )
        .join('-')
        .toLowerCase()
    },
    save() {
      this.isSaving = true
      const pipeline = this.pipeline
      const interval = this.updatedPipeline.interval || this.pipeline.interval
      const transform =
        this.updatedPipeline.transform || this.pipeline.transform
      const kebabName = this.kebabCase(this.updatedPipeline.name)
      const name = kebabName || this.pipeline.name
      const jobId = kebabName || this.pipeline.name
      const pluginNamespace = this.getInstalledPlugin(
        'extractors',
        pipeline.extractor
      ).namespace
      this.updatePipelineSchedule({
        interval,
        transform,
        name,
        jobId,
        pipeline,
        pluginNamespace
      })
        .then(
          () =>
            Vue.toasted.global.success(
              `Pipeline successfully updated - ${pipeline.name}`
            ),
          this.close()
        )
        .catch(error => {
          Vue.toasted.global.error(error.response.data.code)
        })
        .finally(() => {
          this.isSaving = false
        })
    },
    close() {
      this.$router.push({ name: 'pipelines' })
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <h3 class="modal-card-title">Edit a pipeline</h3>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <progress
          v-if="!isLoaded || isSaving"
          class="progress is-small is-info"
        ></progress>
        <div v-else-if="isLoaded" class="columns is-multiline">
          <div class="column is-half">
            <h4>Extractor</h4>
            <div class="control is-expanded">
              <input
                v-model="pipeline.extractor"
                class="input is-fullwidth"
                disabled
              />
            </div>
            <router-link
              :to="{ name: 'extractors' }"
              class="has-text-underlined"
            >
              Manage extractors
            </router-link>
          </div>
          <div class="column is-half">
            <h4>Loader</h4>
            <div class="control is-expanded">
              <input
                v-model="pipeline.loader"
                class="full-width input"
                disabled
              />
            </div>
            <router-link :to="{ name: 'loaders' }" class="has-text-underlined">
              Manage loaders
            </router-link>
          </div>
          <div class="column is-half">
            <h4>Transform</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <!-- <select
                  :value="pipeline.transform"
                  @change="inputUpdate('transform', $event)"
                > -->
                <select
                  v-model="pipeline.transform"
                  @change="inputUpdate('transform', $event)"
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
            <h4>Interval</h4>
            <div class="control is-expanded">
              <span class="select is-fullwidth">
                <!-- <select
                  :value="pipeline.interval"
                  @change="inputUpdate('interval', $event)"
                > -->
                <select
                  v-model="pipeline.interval"
                  @change="inputUpdate('interval', $event)"
                >
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
          <div class="column is-half">
            <h4>Name</h4>
            <div class="control is-expanded">
              <!-- <input
                :value="pipeline.name"
                class="input is-fullwidth"
                type="text"
                @input="inputUpdate('name', $event)"
              /> -->
              <input
                v-model="pipeline.name"
                class="input is-fullwidth"
                type="text"
                @input="inputUpdate('name', $event)"
              />
            </div>
          </div>
          <div class="column is-full">
            <p class="has-text-grey">
              Warning: Changing the job name will modify incremental tracking.
              If the new name does not exist, all refreshes will be rerun from
              the defined job state. State from the prior name `{{
                pipeline.name
              }}` will not be referenced for this schedule going forward.
            </p>
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
