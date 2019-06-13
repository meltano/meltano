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

    <div class="box">

      <table class="table pipelines-table is-fullwidth">
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

          <template v-for="pipeline in [{id: 1}, {id: 2}]">
            <div :key='pipeline.id'>Pipeline {{pipeline.id}}</div>
          </template>

        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'PipelineSchedules',
  computed: {
    ...mapState('configuration', [
      'pipelines',
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
</style>
