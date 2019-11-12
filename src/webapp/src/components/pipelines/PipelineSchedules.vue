<script>
import { mapActions, mapGetters, mapState } from 'vuex'
import Vue from 'vue'

import Dropdown from '@/components/generic/Dropdown'
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'
import utils from '@/utils/utils'

export default {
  name: 'PipelineSchedules',
  components: {
    Dropdown,
    ScheduleTableHead
  },
  computed: {
    ...mapState('configuration', ['pipelines']),
    ...mapGetters('configuration', ['getHasPipelines']),
    ...mapGetters('plugins', ['getIsPluginInstalled']),
    getFormattedDateStringYYYYMMDD() {
      return val => utils.formatDateStringYYYYMMDD(val)
    }
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      if (from.name === 'transforms') {
        vm.goToCreatePipeline()
      }
    })
  },
  created() {
    this.$store.dispatch('configuration/getAllPipelineSchedules')
  },
  methods: {
    ...mapActions('configuration', ['deletePipelineSchedule']),
    deletePipeline(pipeline) {
      this.deletePipelineSchedule(pipeline)
        .then(() =>
          Vue.toasted.global.success(
            `Pipeline Successfully Removed - ${pipeline.name}`
          )
        )
        .catch(error => Vue.toasted.global.error(error.response.data.code))
    },
    goToCreatePipeline() {
      this.$router.push({ name: 'createSchedule' })
    },
    goToLog(jobId) {
      this.$router.push({ name: 'runLog', params: { jobId } })
    },
    runELT(pipeline) {
      this.$store.dispatch('configuration/run', pipeline)
    }
  }
}
</script>

<template>
  <div>
    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class="content has-text-centered">
          <p class="level-item buttons">
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Create a data pipeline below</span>
            </a>
            <span class="step-spacer">then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span
                >Click <span class="is-italic">Manual Run</span> to start data
                collection</span
              >
            </a>
          </p>
        </div>
      </div>
    </div>

    <br />

    <div class="columns is-vcentered">
      <div class="column">
        <h2 class="title is-5">Pipelines</h2>
      </div>

      <div class="column">
        <div class="field is-pulled-right">
          <div class="control">
            <button
              class="button is-interactive-primary"
              @click="goToCreatePipeline()"
            >
              <span>Create</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="getHasPipelines" class="box">
      <table class="table is-fullwidth is-narrow is-hoverable">
        <ScheduleTableHead has-actions has-start-date />

        <tbody>
          <template v-for="pipeline in pipelines">
            <tr :key="pipeline.name">
              <td>
                <p>{{ pipeline.name }}</p>
              </td>
              <td>
                <p class="has-text-centered">{{ pipeline.extractor }}</p>
              </td>
              <td>
                <p class="has-text-centered">{{ pipeline.loader }}</p>
              </td>
              <td>
                <p class="has-text-centered">{{ pipeline.transform }}</p>
              </td>
              <td>
                <p class="has-text-centered">
                  <span v-if="getIsPluginInstalled('orchestrators', 'airflow')">
                    {{ pipeline.interval }}
                  </span>
                  <router-link
                    v-else
                    class="button is-small tooltip"
                    data-tooltip="Airflow Orchestrator must be installed for intervaled runs."
                    :to="{ name: 'orchestration' }"
                  >
                    <span>{{ pipeline.interval }}</span>
                    <span class="icon is-small has-text-warning">
                      <font-awesome-icon
                        icon="exclamation-triangle"
                      ></font-awesome-icon>
                    </span>
                  </router-link>
                </p>
              </td>
              <td>
                <p class="has-text-centered">
                  {{
                    pipeline.startDate
                      ? getFormattedDateStringYYYYMMDD(pipeline.startDate)
                      : 'None'
                  }}
                </p>
              </td>
              <td>
                <p class="has-text-centered">
                  <button
                    class="button is-outlined is-small"
                    :class="{
                      'tooltip is-tooltip-left': pipeline.jobId,
                      'is-danger': pipeline.hasError
                    }"
                    data-tooltip="View this ELT Pipeline's last run logging status."
                    :disabled="!pipeline.jobId"
                    @click="goToLog(pipeline.jobId)"
                  >
                    {{ pipeline.isRunning ? 'Running...' : 'Log' }}
                  </button>
                </p>
              </td>
              <td>
                <div class="buttons is-right">
                  <a
                    class="button is-interactive-primary is-outlined is-small tooltip is-tooltip-left"
                    :class="{ 'is-loading': pipeline.isRunning }"
                    data-tooltip="Run this ELT pipeline once."
                    @click="runELT(pipeline)"
                    >Manual Run</a
                  >
                  <router-link
                    v-if="getIsPluginInstalled('orchestrators', 'airflow')"
                    class="button is-interactive-primary is-outlined is-small tooltip is-tooltip-left"
                    data-tooltip="Automate this ELT pipeline with orchestration."
                    :to="{ name: 'orchestration' }"
                    >Orchestrate</router-link
                  >
                  <router-link
                    class="button is-interactive-primary is-outlined is-small tooltip is-tooltip-left"
                    data-tooltip="Analyze associated models."
                    :to="{ name: 'model' }"
                    >Model</router-link
                  >
                  <Dropdown
                    button-classes="is-small is-danger is-outlined"
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
                          <button
                            class="button is-text"
                            data-dropdown-auto-close
                          >
                            Cancel
                          </button>
                          <button
                            class="button is-danger"
                            data-dropdown-auto-close
                            @click="deletePipeline(pipeline)"
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

    <div v-else class="content">
      <p>
        There are no pipelines scheduled yet.
        <router-link to="schedules/create"
          >Schedule your first Pipeline</router-link
        >
        now.
      </p>
    </div>
  </div>
</template>

<style lang="scss"></style>
