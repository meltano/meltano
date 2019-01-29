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
            {{activeDashboard.name}} with reportIds:
            <ul>
              <li v-for="reportId in activeDashboard.reportIds" :key="reportId">Id: {{reportId}}</li>
            </ul>
            <button @click="saveReportToDashboard">TEMP ADD REPORT ID b47ff6b36e00440b9b0dfb3076537425</button>
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
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'dashboards',
      'isAddDashboard',
      'saveDashboardSettings',
    ]),
  },
  methods: {
    ...mapActions('dashboards', [
      'getDashboards',
      'getDashboard',
      'setAddDashboard',
    ]),
    isActive(dashboard) {
      return dashboard.id === this.activeDashboard.id;
    },
    saveDashboard() {
      this.$store.dispatch('dashboards/saveDashboard', this.saveDashboardSettings);
    },
    saveReportToDashboard() {
      this.$store.dispatch('dashboards/saveReportToDashboard', {reportId: 'b47ff6b36e00440b9b0dfb3076537425', dashboardId: this.activeDashboard.id});
    },
  },
};

</script>

<style lang="scss" scoped>
</style>
