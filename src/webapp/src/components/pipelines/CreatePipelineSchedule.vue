<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import _ from 'lodash'

import ExtractorList from '@/components/pipelines/ExtractorList'

export default {
  name: 'CreatePipelineSchedule',
  components: {
    ExtractorList
  },
  data() {
    return {
      extractorInFocus: null,
      intervalOptions: [
        '@once',
        '@hourly',
        '@daily',
        '@weekly',
        '@monthly',
        '@yearly'
      ],
      isSaving: false,
      isValidConfig: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: 'target-postgres', // Refactor vs. hard code when we again want to display in the UI
        transform: 'run', // Refactor vs. hard code when we again want to display in the UI
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
    ...mapGetters('plugins', ['getIsPluginInstalled']),
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
      'run',
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
      this.pipeline.interval = !_.isEmpty(this.intervalOptions)
        ? this.intervalOptions[0]
        : ''
      this.pipeline.isRunning = false
    },
    save() {
      this.isSaving = true
      const newPipeline = Object.assign({}, this.pipeline)
      this.savePipelineSchedule(newPipeline)
        .then(() => {
          const savedPipeline = this.getPipelineWithExtractor(
            newPipeline.extractor
          )
          this.run(savedPipeline).then(() => {
            Vue.toasted.global.success(`Schedule Saved - ${savedPipeline.name}`)
            Vue.toasted.global.success(`Auto Running - ${savedPipeline.name}`)
            this.$router.push({
              name: 'runLog',
              params: { jobId: savedPipeline.jobId }
            })
          })
        })
        .catch(error => {
          Vue.toasted.global.error(error.response.data.code)
        })
        .finally(() => {
          this.isSaving = false
          this.prepareForm()
        })
    },
    validateConfiguration(configuration) {
      const configSettings = {
        config: configuration.profiles[0].config, // TODO refactor when we reintroduce profiles
        settings: configuration.settings
      }

      this.isValidConfig = this.getHasValidConfigSettings(
        configSettings,
        this.extractorInFocus.settingsGroupValidation
      )
    }
  }
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-narrow">
      <thead>
        <tr>
          <th>
            <div>
              <small class="has-text-interactive-navigation">Step 1</small>
            </div>
            <span>Data Sources</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="The integration or custom data source to connect to"
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
          <th>
            <div>
              <small class="has-text-interactive-navigation">Step 2</small>
            </div>
            <span>Update Interval</span>
            <span
              class="icon has-text-grey-light tooltip is-tooltip-right"
              data-tooltip="How frequently this dataset should be updated"
            >
              <font-awesome-icon icon="info-circle"></font-awesome-icon>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <ExtractorList
              :focused-extractor="extractorInFocus"
              @select="onSelected"
            />
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
          </td>
          <td class="is-vertical-align-baseline">
            <div class="field mt1r">
              <div class="control is-expanded">
                <span
                  class="select is-medium is-fullwidth"
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
            </div>
            <div class="field">
              <a
                class="button is-block is-medium is-interactive-primary tooltip is-tooltip-left"
                data-tooltip="Create integration or custom data connection."
                :class="{ 'is-loading': isSaving }"
                :disabled="!isSaveable"
                @click="save"
                >Save</a
              >
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss"></style>
