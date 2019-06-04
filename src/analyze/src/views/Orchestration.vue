<template>
  <router-view-layout>

    <airflow v-if='isAirflowInstalled'></airflow>
    <div v-else>
      <div class="content">
        <p>Airflow installation is required.</p>
        <p>Until this installation is automatic please follow the <a target='_blank' href="https://www.meltano.com/docs/meltano-cli.html#installing-airflow">Installing Airflow</a> documentation.</p>
      </div>
    </div>

  </router-view-layout>
</template>

<script>
import Airflow from '@/components/Airflow';
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

<style lang="scss" scoped>
</style>
