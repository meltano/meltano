<script>
import { mapState, mapActions } from 'vuex';
import Chart from '@/components/analyze/Chart';
import NewDashboardModal from '@/components/dashboards/NewDashboardModal';
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'Dashboards',
  created() {
    this.initialize(this.$route.params.slug);
  },
  data() {
    return {
      isNewDashboardModalOpen: false,
    };
  },
  components: {
    Chart,
    NewDashboardModal,
    RouterViewLayout,
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'reports',
    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'setDashboard',
      'getActiveDashboardReportsWithQueryResults',
    ]),
    isActive(dashboard) {
      return dashboard.id === this.activeDashboard.id;
    },
    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen;
    },
  },
  watch: {
    activeDashboard() {
      this.getActiveDashboardReportsWithQueryResults();
    },
  },
};

</script>

<template>
  <router-view-layout>

    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class='is-marginless'>Dashboards</h1>
        </div>
      </div>
    </div>

    <div class="container view-body is-fluid">
      <section>
        <div class="columns is-gapless">
          <aside class="column is-one-quarter">
            <nav class="panel has-background-white">
              <p class="panel-heading">
                Dashboards
              </p>

              <div class='panel-block'>
                <a class='button is-secondary is-fullwidth'
                    @click="toggleNewDashboardModal">New Dashboard</a>
              </div>

              <div v-for="dashboard in dashboards"
                  class='panel-block'
                  :class="{'is-active': isActive(dashboard)}"
                  :key="dashboard.id"
                  @click="setDashboard(dashboard)">
                <div>
                  <div>{{dashboard.name}}</div>
                </div>
              </div>

            </nav>
          </aside>
          <div class="column is-three-quarters">

            <h1>{{activeDashboard.name}}</h1>
            <h2 v-if="activeDashboard.description">{{activeDashboard.description}}</h2>
            <hr v-if="activeDashboardReports.length">
            <div
              class='box'
              v-for="report in activeDashboardReports"
              :key="report.id">
              <p>{{report.name}}</p>
              <chart :chart-type='report.chartType'
                      :results='report.queryResults'
                      :result-aggregates='report.queryResultAggregates'></chart>
            </div>

            <NewDashboardModal v-if="isNewDashboardModalOpen" @close="toggleNewDashboardModal" />
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>

</template>

<style lang="scss" scoped>
</style>
