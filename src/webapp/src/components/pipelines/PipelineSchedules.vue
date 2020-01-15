<script>
import { mapActions, mapState } from 'vuex'
import Vue from 'vue'

import AnalyzeList from '@/components/analyze/AnalyzeList'
import Dropdown from '@/components/generic/Dropdown'
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'
import utils from '@/utils/utils'

export default {
  name: 'PipelineSchedules',
  components: {
    AnalyzeList,
    Dropdown,
    ScheduleTableHead
  },
  computed: {
    ...mapState('orchestration', ['pipelines']),
    getMomentFormatlll() {
      return val => utils.momentFormatlll(val)
    },
    getLastRunLabel() {
      return pipeline => {
        const label = pipeline.endedAt
          ? utils.momentFromNow(pipeline.endedAt)
          : 'Log'
        return pipeline.isRunning ? 'Running...' : label
      }
    },
    getMomentFromNow() {
      return val => utils.momentFromNow(val)
    }
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      if (from.name === 'loaders' || from.name === 'loaderSettings') {
        vm.goToCreatePipeline()
      }
    })
  },
  created() {
    this.$store.dispatch('orchestration/getAllPipelineSchedules')
  },
  methods: {
    ...mapActions('orchestration', ['deletePipelineSchedule']),
    goToCreatePipeline() {
      this.$router.push({ name: 'createPipelineSchedule' })
    },
    goToLog(jobId) {
      this.$router.push({ name: 'runLog', params: { jobId } })
    },
    removePipeline(pipeline) {
      this.deletePipelineSchedule(pipeline)
        .then(() =>
          Vue.toasted.global.success(
            `Pipeline Successfully Removed - ${pipeline.name}`
          )
        )
        .catch(error => Vue.toasted.global.error(error.response.data.code))
    },
    runELT(pipeline) {
      this.$store.dispatch('orchestration/run', pipeline)
    }
  }
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-narrow is-hoverable is-size-7">
      <ScheduleTableHead has-actions has-start-date />

      <tbody>
        <template v-for="pipeline in pipelines">
          <tr :key="pipeline.name">
            <td>
              <p>{{ pipeline.name }}</p>
            </td>
            <td>
              <p class="has-text-centered">
                <span>{{ pipeline.interval }}</span>
              </p>
            </td>
            <td>
              <p class="has-text-centered">
                <span
                  :class="{
                    'tooltip is-tooltip-left': pipeline.jobId
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
              <p class="has-text-centered">
                <button
                  class="button is-outlined is-small is-fullwidth h-space-between"
                  :class="{
                    'tooltip is-tooltip-left': pipeline.jobId
                  }"
                  :data-tooltip="
                    `${
                      pipeline.endedAt
                        ? getMomentFormatlll(pipeline.endedAt)
                        : 'View the last run of this ELT pipeline.'
                    }`
                  "
                  :disabled="!pipeline.jobId"
                  @click="goToLog(pipeline.jobId)"
                >
                  <span>
                    {{ getLastRunLabel(pipeline) }}
                  </span>
                  <span
                    v-if="!pipeline.isRunning"
                    class="icon is-small"
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
              </p>
            </td>
            <td>
              <div class="buttons is-right">
                <a
                  class="button is-small tooltip is-tooltip-left"
                  :class="{ 'is-loading': pipeline.isRunning }"
                  data-tooltip="Run this ELT pipeline once."
                  @click="runELT(pipeline)"
                  >Manual Run</a
                >
                <Dropdown
                  label="Reports"
                  button-classes="is-interactive-primary is-outlined is-small"
                  :tooltip="{
                    classes: 'is-tooltip-left',
                    message: 'Analyze related reports of this pipeline.'
                  }"
                  menu-classes="dropdown-menu-300"
                  icon-open="chart-line"
                  icon-close="caret-down"
                  is-right-aligned
                >
                  <div class="dropdown-content is-unselectable">
                    <AnalyzeList :pipeline="pipeline"></AnalyzeList>
                  </div>
                </Dropdown>
                <Dropdown
                  :button-classes="
                    `is-small is-danger is-outlined ${
                      pipeline.isDeleting ? 'is-loading' : ''
                    }`
                  "
                  :disabled="pipeline.isRunning"
                  :tooltip="{
                    classes: 'is-tooltip-left',
                    message: 'Delete this ELT Pipeline'
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
