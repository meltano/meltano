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
      <table class="table pipelines-table is-fullwidth is-narrow is-hoverable">
        <thead>
          <tr>
            <th>Name</th>
            <th class='has-text-centered'>Extractor</th>
            <th class='has-text-centered'>Loader</th>
            <th class='has-text-centered'>Transform</th>
            <th class='has-text-centered'>Interval</th>
            <th class='has-text-centered'>Catch-up Date</th>
            <th class='has-text-centered'></th>
          </tr>
        </thead>
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
                <p class='has-text-centered'>{{pipeline.startDate || 'None'}}</p>
              </td>
              <td>
                <div class="buttons is-right">
                  <button
                    class="button is-small tooltip is-tooltip-left"
                    disabled
                    data-tooltip="Not implemented">Edit</button>
                </div>
              </td>

            </tr>

          </template>

        </tbody>
      </table>
    </div>

    <div v-else class='content'>
      <p>There are no pipelines scheduled yet. <router-link to='schedule/create'>Schedule your first Pipeline</router-link> now.</p>
    </div>

  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'PipelineSchedules',
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
  },
  methods: {
    createPipeline() {
      this.$router.push({ name: 'createSchedule' });
    },
  },
};
</script>

<style lang="scss">
.pipelines-table {
  td {
    vertical-align: middle;
  }
}
</style>
