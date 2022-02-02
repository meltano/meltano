<script>
import { mapActions, mapGetters } from 'vuex'
import Vue from 'vue'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import Dropdown from '@/components/generic/Dropdown'
import ExploreButton from '@/components/analyze/ExploreButton'
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'
import { PIPELINE_INTERVAL_OPTIONS, TRANSFORM_OPTIONS } from '@/utils/constants'
import utils from '@/utils/utils'
import capitalize from '@/filters/capitalize'

export default {
  name: 'PipelineSchedules',
  components: {
    ConnectorLogo,
    Dropdown,
    ExploreButton,
    ScheduleTableHead
  },
  filters: {
    capitalize
  },
  props: {
    pipelines: { type: Array, required: true, default: () => [] }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin', 'getPluginLabel']),
    intervalOptions() {
      return PIPELINE_INTERVAL_OPTIONS
    },
    transformOptions() {
      return TRANSFORM_OPTIONS
    },
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
    },
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
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
    onChangeItem(option, pipeline, item) {
      const newPipelineValue = option.srcElement.selectedOptions[0].value
      if (newPipelineValue !== pipeline[item]) {
        const pluginNamespace = this.getInstalledPlugin(
          'extractors',
          pipeline.extractor
        ).namespace
        this.updatePipelineSchedule({
          [item]: newPipelineValue,
          pipeline,
          pluginNamespace
        })
          .then(() =>
            Vue.toasted.global.success(
              `Pipeline successfully updated - ${pipeline.name}`
            )
          )
          .catch(this.$error.handle)
      }
    },
    setCRONInterval() {
      this.$router.push({ name: 'cronJobSettings' })
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
    <table class="table is-fullwidth is-hoverable is-size-7">
      <ScheduleTableHead has-actions has-start-date />
      <tbody>
        <template v-for="pipeline in pipelines">
          <tr :key="pipeline.name">
            <td>
              {{ pipeline.name }}
            </td>
            <td>
              <article class="media is-vcentered">
                <figure class="media-left">
                  <p class="image level-item is-32x32 container">
                    <ConnectorLogo :connector="pipeline.extractor" />
                  </p>
                </figure>
                <div class="media-content">
                  <div class="content">
                    <p>
                      <strong>
                        {{ getPluginLabel('extractors', pipeline.extractor) }}
                      </strong>
                    </p>
                  </div>
                </div>
              </article>
            </td>
            <td>
              {{ getPluginLabel('loaders', pipeline.loader) }}
            </td>
            <td>
              <div class="is-flex is-vcentered">
                <div class="field has-addons">
                  <div class="control is-expanded">
                    <span
                      class="select is-fullwidth is-size-7"
                      :class="{
                        'is-loading': getIsDisabled(pipeline)
                      }"
                    >
                      <select
                        :value="pipeline.transform"
                        :disabled="getIsDisabled(pipeline)"
                        @change="onChangeItem($event, pipeline, 'transform')"
                      >
                        <option
                          v-for="option in transformOptions"
                          :key="option"
                          :value="option"
                          >{{ option | capitalize }}</option
                        >
                      </select>
                    </span>
                  </div>
                </div>
              </div>
            </td>
            <td>
              <div class="is-flex is-vcentered">
                <div class="field has-addons">
                  <div class="control is-expanded">
                    <span
                      class="select is-fullwidth is-size-7"
                      :class="{
                        'is-loading': getIsDisabled(pipeline)
                      }"
                    >
                      <select
                        :disabled="getIsDisabled(pipeline)"
                        :value="pipeline.interval"
                        @input="onChangeItem($event, pipeline, 'interval')"
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
                  class="button is-small is-outlined is-fullwidth h-space-between"
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
              <div class="buttons">
                <button
                  class="button is-small tooltip is-tooltip-top is-info"
                  :class="{ 'is-loading': pipeline.isRunning }"
                  :disabled="getIsDisabled(pipeline)"
                  data-tooltip="Manually run this pipeline once"
                  @click="runELT(pipeline)"
                >
                  <span>Run Now</span>
                  <span class="icon is-small">
                    <font-awesome-icon icon="rocket"></font-awesome-icon>
                  </span>
                </button>
                <ExploreButton
                  :pipeline="pipeline"
                  is-tooltip-left
                  custom-class="is-small"
                />
                <div v-if="pipeline.interval === '@other'" class="control">
                  <button
                    class="button is-small tooltip is-tooltip-right is-info"
                    data-tooltip="Set the CRON interval you'd like"
                    @click="setCRONInterval()"
                  >
                    Set Interval
                  </button>
                </div>
                <Dropdown
                  :button-classes="
                    `is-small is-danger is-outlined ${
                      pipeline.isDeleting ? 'is-loading' : ''
                    }`
                  "
                  :disabled="getIsDisabled(pipeline)"
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
                      <div class="buttons is-right ">
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
    <div v-if="isModal">
      <router-view :name="getModalName"></router-view>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.buttons {
  justify-content: space-evenly;
}
</style>
