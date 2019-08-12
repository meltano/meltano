<script>
import { mapGetters, mapState } from 'vuex'

import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'

import utils from '@/utils/utils'

export default {
  name: 'PipelineSchedules',
  components: {
    ScheduleTableHead
  },
  created() {
    this.$store.dispatch('configuration/getAllPipelineSchedules')
    if (!this.getHasPipelines) {
      this.createPipeline()
    }
  },
  computed: {
    ...mapState('configuration', ['pipelines']),
    ...mapGetters('configuration', ['getHasPipelines']),
    ...mapGetters('plugins', ['getIsPluginInstalled']),
    getFormattedDateStringYYYYMMDD() {
      return val => utils.formatDateStringYYYYMMDD(val)
    }
  },
  methods: {
    createPipeline() {
      this.$router.push({ name: 'createSchedule' })
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
                >Click <span class="is-italic">Run</span> to schedule it</span
              >
            </a>
          </p>
        </div>
      </div>
    </div>

    <br />

    <div class="columns is-vcentered">
      <div class="column">
        <h2 class="title is-5">Existing</h2>
      </div>

      <div class="column">
        <div class="field is-pulled-right">
          <div class="control">
            <button
              class="button is-interactive-primary"
              @click="createPipeline()"
            >
              <span>Create</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="getHasPipelines" class="box">
      <table class="table is-fullwidth is-narrow is-hoverable">
        <ScheduleTableHead has-actions />

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
                <div class="buttons is-right">
                  <router-link
                    v-if="getIsPluginInstalled('orchestrators', 'airflow')"
                    class="button is-interactive-primary is-outlined is-small"
                    :to="{ name: 'orchestration' }"
                    >Orchestration</router-link
                  >
                  <a
                    class="button is-interactive-primary is-outlined is-small tooltip is-tooltip-left"
                    :class="{ 'is-loading': pipeline.isRunning }"
                    data-tooltip="Run this ELT definition once without scheduling."
                    @click="runELT(pipeline)"
                    >Run</a
                  >
                  <router-link
                    class="button is-interactive-primary is-outlined is-small"
                    :to="{ name: 'analyze' }"
                    >Analyze</router-link
                  >
                  <a
                    :disabled="pipeline.isRunning"
                    class="button is-small tooltip is-tooltip-warning is-tooltip-multiline is-tooltip-left"
                    data-tooltip="This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues."
                    >Edit</a
                  >
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
