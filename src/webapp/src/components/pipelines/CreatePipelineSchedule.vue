<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import _ from 'lodash'

import Dropdown from '@/components/generic/Dropdown'
import ExtractorList from '@/components/pipelines/ExtractorList'

export default {
  name: 'CreatePipelineSchedule',
  components: {
    Dropdown,
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
      'getHasValidConfigSettings'
    ]),
    ...mapGetters('plugins', ['getIsPluginInstalled']),
    ...mapState('orchestration', ['extractorInFocusConfiguration']),
    getDataSourceLabel() {
      return this.extractorInFocus ? this.extractorInFocus.label : 'None'
    },
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
    this.$store.dispatch('plugins/getInstalledPlugins').then(this.prefillForm)
  },
  methods: {
    ...mapActions('orchestration', [
      'getExtractorConfiguration',
      'run',
      'savePipelineSchedule'
    ]),
    checkConfiguration(extractorName) {
      this.isValidConfig = false
      const isInstalled = this.getIsPluginInstalled('extractors', extractorName)
      if (isInstalled) {
        this.getExtractorConfiguration(extractorName).then(
          this.validateConfiguration
        )
      }
    },
    onSelected(extractor) {
      this.extractorInFocus = extractor
      this.pipeline.extractor = this.extractorInFocus.name
      this.checkConfiguration(this.pipeline.extractor)
      this.$refs['datasets-dropdown'].close()
    },
    prefillForm() {
      this.pipeline.name = `pipeline-${new Date().getTime()}`
      this.pipeline.interval = !_.isEmpty(this.intervalOptions)
        ? this.intervalOptions[0]
        : ''
    },
    save() {
      this.isSaving = true
      this.savePipelineSchedule(this.pipeline)
        .then(() => {
          this.run(this.pipeline).then(() => {
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
    },
    validateConfiguration(configuration) {
      const configSettings = {
        config: configuration.profiles[0].config, // TODO refactor when we reintroduce profiles
        settings: configuration.settings
      }
      const isValid = this.getHasValidConfigSettings(
        configSettings,
        this.extractorInFocus.settingsGroupValidation
      )
      this.isValidConfig = isValid
    }
  }
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-narrow is-hoverable">
      <thead>
        <tr>
          <th>
            <div>
              <small class="has-text-interactive-navigation">Step 1</small>
              <small v-if="!isValidConfig" class="is-italic has-text-warning">
                Needs configuration</small
              >
            </div>
            <span>Data Source</span>
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
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <Dropdown
              ref="datasets-dropdown"
              :label="getDataSourceLabel"
              button-classes="is-outlined"
              :label-classes="isValidConfig ? 'has-text-success' : ''"
              :tooltip="{
                classes: 'is-tooltip-right',
                message:
                  'Select an integration or custom data source to connect to'
              }"
              menu-classes="dropdown-menu-600"
              is-full-width
            >
              <div class="dropdown-content is-unselectable">
                <ExtractorList @select="onSelected" />
              </div>
            </Dropdown>
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
                  <option v-for="interval in intervalOptions" :key="interval">{{
                    interval
                  }}</option>
                </select>
              </span>
            </div>
          </td>
          <td>
            <div class="buttons is-right">
              <a
                class="button is-interactive-primary tooltip is-tooltip-left"
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
