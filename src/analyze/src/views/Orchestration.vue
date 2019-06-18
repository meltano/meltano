<script>
import Airflow from '@/components/orchestration/Airflow';
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'Orchestration',
  components: {
    Airflow,
    RouterViewLayout,
  },
  computed: {
    isAirflowInstalled() {
      return Boolean(FLASK.airflowUrl);
    },
  },
};

</script>

<template>
  <router-view-layout>

    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class='is-marginless'>Orchestration</h1>
        </div>
      </div>
    </div>

    <div class="container view-body">
      <airflow v-if='isAirflowInstalled'></airflow>
      <section v-else>
        <div class="columns">
          <div class="column">
            <div class="content">
              <p class='is-italic'>Airflow installation is required.</p>
              <p>Until this installation is automatic please follow the <a target='_blank' href="https://www.meltano.com/docs/meltano-cli.html#installing-airflow">Installing Airflow</a> documentation.</p>
            </div>
          </div>
        </div>
      </section>
    </div>

  </router-view-layout>
</template>

<style lang="scss" scoped>
</style>
