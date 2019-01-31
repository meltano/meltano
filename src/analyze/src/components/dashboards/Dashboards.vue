<template>
  <div class="container">
    <section class="section">
      <div class="columns">

        <nav class="panel column is-one-quarter">
          <p class="panel-heading">
            Dashboards
          </p>
          <div class="panel-block">
            <div class="inner-scroll text-selection-off">
              <ul>
                <li><a @click="setAddDashboard(true)">Add Dashboard</a></li>
                <li v-for="dashboard in dashboards"
                    :class="{'is-active': isActive(dashboard)}"
                    :key="dashboard.id"
                    @click="getDashboard(dashboard)">
                  <a>{{dashboard.name}}</a>
                  <div v-if="dashboard.id === activeDashboard.id" style="margin-left: 15px;">
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
                </li>
              </ul>
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
            <div v-for="report in reports" :key="report.id">
              <div v-if="isReportInActiveDashboard(report)">
                <p>Graph: {{report.name}}</p>
                <p>queryPayload: {{report.queryPayload}}</p>
                <p>chartType: {{report.chartType}}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Dashboards',
  created() {
    this.getDashboards();
    this.getReports();
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
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
};

</script>

<style lang="scss" scoped>
</style>
