<template>
  <div class="container">
    <section class="section">
      <div class="columns">

        <nav class="panel column is-one-quarter">
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

        <div class="column is-three-quarters">

          <div v-if="isAddDashboard">
            <div class="field">
              <label class="label">Name</label>
              <div class="control">
                <input class="input"
                        type="text"
                        placeholder="Name your dashboard"
                        v-model="saveDashboardSettings.name">
              </div>
            </div>
            <div class="field">
              <label class="label">Description</label>
              <div class="control">
                <textarea class="textarea"
                          placeholder="Describe your dashboard for easier reference later"
                          v-model="saveDashboardSettings.description"></textarea>
              </div>
            </div>
            <div class="field is-grouped">
              <div class="control">
                <button class="button is-link" @click="saveDashboard">Save</button>
              </div>
            </div>
          </div>

          <div v-if="!isAddDashboard">
            <h1><strong>{{activeDashboard.name}}</strong></h1>
            <div v-for="report in activeDashboardReports" :key="report.id">
              <p>{{report.name}}</p>
              <chart :chart-type='report.chartType'
                      :results='report.queryResults'
                      :result-aggregates='[]'></chart>
            </div>
          </div>
        </div>

      </div>
    </section>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import Chart from '../designs/Chart';

export default {
  name: 'Dashboards',
  created() {
    this.getDashboards();
    this.getReports();
  },
  components: {
    Chart,
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'isAddDashboard',
      'reports',
      'saveDashboardSettings',
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
    saveDashboard() {
      this.$store.dispatch('dashboards/saveDashboard', this.saveDashboardSettings);
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
