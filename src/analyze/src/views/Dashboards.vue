<template>
  <router-view-layout>

    <div slot='left'>

      <nav class="panel">
        <p class="panel-heading">
          Dashboards
        </p>

        <div class='panel-block'>
          <a class='button is-secondary is-fullwidth'
              @click="setAddDashboard(true)">Create Dashboard</a>
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
                  <label for="'checkbox-' + report.id"
                          @click="toggleReportInDashboard(report)">
                    <input type="checkbox"
                          :id="'checkbox-' + report.id"
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
      <div v-if="isAddDashboard">
        <CreateDashboard />
      </div>

      <div v-if="!isAddDashboard">
        <h1><strong>{{activeDashboard.name}}</strong></h1>
        <div v-for="report in activeDashboardReports" :key="report.id">
          <p>{{report.name}}</p>
          <chart :chart-type='report.chartType'
                  :results='report.queryResults'
                  :result-aggregates='report.queryResultAggregates'></chart>
        </div>
      </div>
    </div>

  </router-view-layout>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import RouterViewLayout from '@/views/RouterViewLayout';
import Chart from '../components/designs/Chart';
import CreateDashboard from '../components/dashboards/CreateDashboard';

export default {
  name: 'Dashboards',
  created() {
    this.getDashboards();
    this.getReports();
  },
  components: {
    Chart,
    CreateDashboard,
    RouterViewLayout,
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'isAddDashboard',
      'reports',
    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboards',
      'getDashboard',
      'getReports',
      'getActiveDashboardReportsWithQueryResults',
      'setAddDashboard',
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
