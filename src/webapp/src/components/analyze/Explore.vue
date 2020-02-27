<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'Explore',
  data() {
    return {
      hasLoadedDashboards: false,
      hasLoadedReports: false,
      namespace: '',
      title: 'Explore'
    }
  },
  computed: {
    ...mapState('dashboards', ['dashboards']),
    ...mapState('reports', ['reports']),
    getFilteredDashboards() {
      // TODO in order for filtering to work we need to do a dashboard version/migration and provide a namespace key
      return this.dashboards//.filter(dashboard => dashboard.namespace === this.namespace)
    },
    getFilteredReports() {
      return this.reports.filter(report => report.namespace === this.namespace)
    }
  },
  created() {
    this.namespace = this.$route.params.namespace
    this.getDashboards().then(() => (this.hasLoadedDashboards = true))
    this.getReports().then(() => (this.hasLoadedReports = true))
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards']),
    ...mapActions('reports', ['getReports']),
    goToDashboard(dashboard) {
      this.$router.push({ name: 'dashboard', params: dashboard })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    }
  }
}
</script>

<template>
  <div>
    <h2 id="explore" class="title">{{ title }}</h2>

    <div class="columns">
      <!-- Report Templates -->
      <div class="column">
        <div class="content">
          <h3 id="report-templates" class="title">Report Templates</h3>
        </div>
        <div class="box">
          <progress v-if="true" class="progress is-small is-info"></progress>
          <template v-else>
            ...
          </template>
        </div>
      </div>

      <!-- Reports -->
      <div class="column">
        <div class="content">
          <h3 id="reports" class="title">Reports</h3>
        </div>
        <div class="box">
          <progress
            v-if="!hasLoadedReports"
            class="progress is-small is-info"
          ></progress>
          <template v-else-if="reports.length">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="report in getFilteredReports"
                :key="report.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToReport(report)"
              >
                <div>
                  {{ report.name }}
                </div>
                <div>
                  <button class="button is-small is-pulled-right">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No reports</p></div>
          </template>
        </div>
      </div>

      <!-- Dashboards -->
      <div class="column">
        <div class="content">
          <h3 id="dashboards" class="title">Dashboards</h3>
        </div>
        <div class="box">
          <progress
            v-if="!hasLoadedDashboards"
            class="progress is-small is-info"
          ></progress>
          <template v-else-if="dashboards.length">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="dashboard in getFilteredDashboards"
                :key="dashboard.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToDashboard(dashboard)"
              >
                <div>
                  {{ dashboard.name }}
                </div>
                <div>
                  <button class="button is-small is-pulled-right">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No dashboards</p></div>
          </template>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
