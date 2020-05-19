<script>
import { mapActions, mapGetters } from 'vuex'
import Vue from 'vue'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import Dropdown from '@/components/generic/Dropdown'
import ExploreButton from '@/components/analyze/ExploreButton'
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'
import utils from '@/utils/utils'

export default {
  name: 'PipelineSchedules',
  components: {
    ConnectorLogo,
    Dropdown,
    ExploreButton,
    ScheduleTableHead
  },
  props: {
    pipelines: { type: Array, required: true, default: () => [] }
  },
  data() {
    return {
      intervalOptions: {
        '@once': 'Once (Manual)',
        '@hourly': 'Hourly',
        '@daily': 'Daily',
        '@weekly': 'Weekly',
        '@monthly': 'Monthly',
        '@yearly': 'Yearly'
      }
    }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin', 'getPluginLabel']),
    getIsDisabled() {
      return pipeline => pipeline.isRunning || pipeline.isSaving
    },
    getMomentFormatlll() {
      return val => utils.momentFormatlll(val)
    },
    getLastRunLabel() {
      return pipeline => {
        const label = pipeline.endedAt
          ? utils.momentFromNow(pipeline.endedAt)
          : 'Never'
        return pipeline.isRunning ? 'Running...' : label
      }
    },
    getMomentFromNow() {
      return val => utils.momentFromNow(val)
    }
  },
  methods: {
    ...mapActions('orchestration', [
      'deletePipelineSchedule',
      'updatePipelineSchedule'
    ]),
    goToLog(jobId) {
      this.$router.push({ name: 'runLog', params: { jobId } })
    },
    onChangeInterval(option, pipeline) {
      const interval = option.srcElement.selectedOptions[0].value
      if (interval !== pipeline.interval) {
        const pluginNamespace = this.getInstalledPlugin(
          'extractors',
          pipeline.extractor
        ).namespace
        this.updatePipelineSchedule({ interval, pipeline, pluginNamespace })
          .then(() =>
            Vue.toasted.global.success(
              `Pipeline successfully updated - ${pipeline.name}`
            )
          )
          .catch(this.$error.handle)
      }
    },
    removePipeline(pipeline) {
      this.deletePipelineSchedule(pipeline)
        .then(() =>
          Vue.toasted.global.success(
            `Pipeline successfully removed - ${pipeline.name}`
          )
        )
        .catch(this.$error.handle)
    },
    runELT(pipeline) {
      this.$store.dispatch('orchestration/run', pipeline)
    }
  }
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-hoverable">
      <ScheduleTableHead has-actions has-start-date />

      <tbody>
        <template v-for="pipeline in pipelines">
          <tr :key="pipeline.name">
            <td>
              <article class="media">
                <figure class="media-left">
                  <p class="image level-item is-48x48 container">
                    <ConnectorLogo :connector="pipeline.extractor" />
                  </p>
                </figure>
                <div class="media-content">
                  <div class="content">
                    <p>
                      <strong>
                        {{ getPluginLabel('extractors', pipeline.extractor) }}
                      </strong>
                      <br />
                      <small>Default</small>
                    </p>
                  </div>
                </div>
              </article>
            </td>
            <td>
              <div class="is-flex is-vcentered">
                <div class="field has-addons">
                  <div class="control is-expanded">
                    <span
                      class="select is-fullwidth"
                      :class="{
                        'is-loading': getIsDisabled(pipeline)
                      }"
                    >
                      <select
                        :disabled="getIsDisabled(pipeline)"
                        :value="pipeline.interval"
                        @input="onChangeInterval($event, pipeline)"
                      >
                        <option
                          v-for="(label, value) in intervalOptions"
                          :key="value"
                          :value="value"
                          >{{ label }}</option
                        >
                      </select>
                    </span>
                  </div>

                  <div class="control">
                    <button
                      class="button tooltip is-tooltip-right"
                      :class="{ 'is-loading': pipeline.isRunning }"
                      :disabled="getIsDisabled(pipeline)"
                      data-tooltip="Manually run this pipeline once"
                      @click="runELT(pipeline)"
                    >
                      Run Now
                    </button>
                  </div>
                </div>
              </div>
            </td>
            <td>
              <p>
                <span
                  :class="{
                    'tooltip is-tooltip-left': pipeline.hasEverSucceeded
                  }"
                  :data-tooltip="getMomentFormatlll(pipeline.startDate)"
                >
                  <span>
                    {{
                      pipeline.startDate
                        ? getMomentFromNow(pipeline.startDate)
                        : 'None'
                    }}
                  </span>
                </span>
              </p>
            </td>
            <td>
              <p>
                <button
                  v-if="pipeline.isRunning || pipeline.endedAt"
                  class="button is-outlined is-fullwidth h-space-between"
                  :class="{
                    'tooltip is-tooltip-left': pipeline.hasEverSucceeded
                  }"
                  :data-tooltip="
                    `${
                      pipeline.endedAt
                        ? getMomentFormatlll(pipeline.endedAt)
                        : 'View the last run of this ELT pipeline.'
                    }`
                  "
                  @click="goToLog(pipeline.jobId)"
                >
                  <span>
                    {{ getLastRunLabel(pipeline) }}
                  </span>
                  <span
                    v-if="pipeline.endedAt"
                    class="icon"
                    :class="
                      `has-text-${pipeline.hasError ? 'danger' : 'success'}`
                    "
                  >
                    <font-awesome-icon
                      :icon="
                        pipeline.hasError
                          ? 'exclamation-triangle'
                          : 'check-circle'
                      "
                    ></font-awesome-icon>
                  </span>
                </button>
                <span v-else>Never</span>
              </p>
            </td>
            <td>
              <div class="buttons is-right">
                <ExploreButton :pipeline="pipeline" is-tooltip-left />
                <Dropdown
                  :button-classes="
                    `is-danger is-outlined ${
                      pipeline.isDeleting ? 'is-loading' : ''
                    }`
                  "
                  :disabled="getIsDisabled(pipeline)"
                  :tooltip="{
                    classes: 'is-tooltip-left',
                    message: 'Delete this pipeline'
                  }"
                  menu-classes="dropdown-menu-300"
                  icon-open="trash-alt"
                  icon-close="caret-up"
                  is-right-aligned
                >
                  <div class="dropdown-content is-unselectable">
                    <div class="dropdown-item">
                      <div class="content">
                        <p>
                          Please confirm deletion of pipeline:<br /><em>{{
                            pipeline.name
                          }}</em
                          >.
                        </p>
                      </div>
                      <div class="buttons is-right">
                        <button class="button is-text" data-dropdown-auto-close>
                          Cancel
                        </button>
                        <button
                          class="button is-danger"
                          data-dropdown-auto-close
                          @click="removePipeline(pipeline)"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </Dropdown>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<style lang="scss"></style>
