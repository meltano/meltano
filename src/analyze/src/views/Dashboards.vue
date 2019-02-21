<template>
  <router-view-layout>

    <div slot='left'>

      <nav class="panel">
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
            @click="getDashboard(dashboard)">
          <div>
            <div>{{dashboard.name}}</div>
            <div v-if="dashboard.id === activeDashboard.id">
              <small>Reports ({{activeDashboard.reportIds.length}})</small>
              <ul>
                <li v-for="report in reports" :key="report.id">
                  <label @click="toggleReportInDashboard(report)">
                    <input type="checkbox"
                          :checked="isReportInActiveDashboard(report)">
                    {{report.name}}</label>
                </li>
              </ul>
            </div>
          </div>
        </div>

      </nav>

    </div>

    <div slot='right'>
      <h1><strong>{{activeDashboard.name}}</strong></h1>
      <div v-for="report in activeDashboardReports" :key="report.id">
        <p>{{report.name}}</p>
        <chart :chart-type='report.chartType'
                :results='report.queryResults'
                :result-aggregates='report.queryResultAggregates'></chart>
      </div>

      <!-- New Dashboard Modal -->
      <NewDashboardModal v-if="isNewDashboardModalOpen" @close="toggleNewDashboardModal" />

    </div>

  </router-view-layout>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import RouterViewLayout from '@/views/RouterViewLayout';
import Chart from '../components/designs/Chart';
import NewDashboardModal from '../components/dashboards/NewDashboardModal';

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
      'getDashboard',
      'getReports',
      'getActiveDashboardReportsWithQueryResults',
    ]),
    isActive(dashboard) {
      return dashboard.id === this.activeDashboard.id;
    },
    isReportInActiveDashboard(report) {
      return this.activeDashboard.reportIds.includes(report.id);
    },
    toggleReportInDashboard(report) {
      const methodName = this.isReportInActiveDashboard(report)
        ? 'removeReportFromDashboard'
        : 'addReportToDashboard';
      this.$store.dispatch(`dashboards/${methodName}`, {
        reportId: report.id,
        dashboardId: this.activeDashboard.id,
      });
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

<style lang="scss" scoped>
</style>
