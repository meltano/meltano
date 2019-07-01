<script>
import { mapGetters, mapState } from 'vuex';

import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead';

import utils from '@/utils/utils';

export default {
  name: 'PipelineSchedules',
  components: {
    ScheduleTableHead,
  },
  created() {
    this.$store.dispatch('configuration/getAllPipelineSchedules');
    if (!this.getHasPipelines) {
      this.createPipeline();
    }
  },
  computed: {
    ...mapState('configuration', [
      'pipelines',
    ]),
    ...mapGetters('configuration', [
      'getHasPipelines',
    ]),
    getFormattedDateStringYYYYMMDD() {
      return val => utils.formatDateStringYYYYMMDD(val);
    },
  },
  methods: {
    createPipeline() {
      this.$router.push({ name: 'createSchedule' });
    },
  },
};
</script>

<template>
  <div>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class='content has-text-centered'>
          <p class='level-item buttons'>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Create a data pipeline below</span>
            </a>
            <span class='step-spacer'>then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Click <span class='is-italic'>Run</span> to schedule it</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <br>

    <div class="columns is-vcentered">

      <div class="column">
        <h2 class='title is-5'>Existing</h2>
      </div>

      <div class="column">
        <div class="field is-pulled-right">

          <p class="control">
            <button
              class="button is-interactive-primary"
              @click="createPipeline();">
              <span>Create</span>
            </button>
          </p>

        </div>
      </div>

    </div>

    <div v-if='getHasPipelines' class="box">
      <table class="table is-fullwidth is-narrow is-hoverable">

        <ScheduleTableHead />

        <tbody>

          <template v-for="pipeline in pipelines">
            <tr :key='pipeline.name'>
              <td>
                <p>{{pipeline.name}}</p>
              </td>
              <td>
                <p class='has-text-centered'>{{pipeline.extractor}}</p>
              </td>
              <td>
                <p class='has-text-centered'>{{pipeline.loader}}</p>
              </td>
              <td>
                <p class='has-text-centered'>{{pipeline.transform}}</p>
              </td>
              <td>
                <p class='has-text-centered'>{{pipeline.interval}}</p>
              </td>
              <td>
                <p class='has-text-centered'>{{pipeline.startDate
                  ? getFormattedDateStringYYYYMMDD(pipeline.startDate)
                  : 'None'
                }}</p>
              </td>
              <td>
                <div class="buttons is-right">
                  <router-link
                    class="button is-interactive-primary is-outlined is-small"
                    :to="{name: 'orchestration'}">Orchestration</router-link>
                  <a
                    class='button is-small tooltip is-tooltip-warning is-tooltip-multiline is-tooltip-left'
                    data-tooltip='This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues.'>Edit</a>
                </div>
              </td>

            </tr>

          </template>

        </tbody>
      </table>
    </div>

    <div v-else class='content'>
      <p>There are no pipelines scheduled yet. <router-link to='schedules/create'>Schedule your first Pipeline</router-link> now.</p>
    </div>

  </div>
</template>

<style lang="scss">
</style>
