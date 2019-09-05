<script>
import { mapActions, mapState } from 'vuex'
import Chart from '@/components/analyze/Chart'
import NewDashboardModal from '@/components/dashboards/NewDashboardModal'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboards',
  components: {
    Chart,
    NewDashboardModal,
    RouterViewLayout
  },
  data() {
    return {
      isActiveDashboardLoading: false,
      isInitializing: false,
      isNewDashboardModalOpen: false
    }
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'reports'
    ]),
    isActive() {
      return dashboard => dashboard.id === this.activeDashboard.id
    }
  },
  watch: {
    activeDashboard() {
      this.isActiveDashboardLoading = true
      this.getActiveDashboardReportsWithQueryResults().then(() => {
        this.isActiveDashboardLoading = false
      })
    }
  },
  beforeDestroy() {
    this.$store.dispatch('dashboards/resetActiveDashboard')
    this.$store.dispatch('dashboards/resetActiveDashboardReports')
  },
  created() {
    this.isInitializing = true
    this.initialize(this.$route.params.slug).then(() => {
      this.isInitializing = false
    })
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'updateCurrentDashboard',
      'getActiveDashboardReportsWithQueryResults'
    ]),
    goToDashboard(dashboard) {
      this.updateCurrentDashboard(dashboard).then(() => {
        this.$router.push({ name: 'dashboard', params: dashboard })
      })
    },
    goToDesign(report) {
      const params = { design: report.design, model: report.model }
      this.$router.push({ name: 'analyzeDesign', params })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    },
    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <section>
        <div class="columns">
          <aside class="column is-one-quarter">
            <div class="box">
              <div class="columns is-vcentered">
                <div class="column is-three-fifths">
                  <h2 class="title is-5">Dashboards</h2>
                </div>
                <div class="column is-two-fifths">
                  <div class="buttons is-right">
                    <button
                      class="button is-success"
                      @click="toggleNewDashboardModal"
                    >
                      New
                    </button>
                  </div>
                </div>
              </div>

              <progress
                v-if="isInitializing"
                class="progress is-small is-info"
              ></progress>

              <template v-if="dashboards.length > 0">
                <div class="panel">
                  <a
                    v-for="dashboard in dashboards"
                    :key="dashboard.id"
                    class="panel-block space-between has-text-weight-medium"
                    :class="{ 'is-active': isActive(dashboard) }"
                    @click="goToDashboard(dashboard)"
                  >
                    {{ dashboard.name }}
                  </a>
                </div>
              </template>
            </div>
          </aside>

          <div class="column is-three-quarters">
            <div class="box">
              <template v-if="activeDashboard.name">
                <div class="columns is-vcentered">
                  <div class="column">
                    <h2 class="title is-5">{{ activeDashboard.name }}</h2>
                    <h3 v-if="activeDashboard.description" class="subtitle">
                      {{ activeDashboard.description }}
                    </h3>
                  </div>
                  <div v-if="activeDashboard.name" class="column">
                    <div class="buttons is-right">
                      <a
                        class="button tooltip is-tooltip-warning is-tooltip-multiline is-tooltip-left"
                        data-tooltip="This feature is queued. Feel free to contribute at gitlab.com/meltano/meltano/issues."
                        >Add Report</a
                      >
                    </div>
                  </div>
                </div>

                <progress
                  v-if="isActiveDashboardLoading"
                  class="progress is-small is-info"
                >
                </progress>
                <template v-else>
                  <template v-if="activeDashboardReports.length > 0">
                    <div
                      v-for="report in activeDashboardReports"
                      :key="report.id"
                    >
                      <hr />
                      <div class="level">
                        <div class="level-left">
                          <div class="level-item">
                            <div class="content">
                              <h5 class="has-text-centered">
                                {{ report.name }}
                              </h5>
                            </div>
                          </div>
                        </div>
                        <div class="level-right">
                          <div class="level-item">
                            <div class="buttons">
                              <a
                                class="button is-small"
                                @click="goToReport(report)"
                                >Edit</a
                              >
                              <a
                                class="button is-small"
                                @click="goToDesign(report)"
                                >Explore</a
                              >
                            </div>
                          </div>
                        </div>
                      </div>
                      <chart
                        :chart-type="report.chartType"
                        :results="report.queryResults"
                        :result-aggregates="report.queryResultAggregates"
                      ></chart>
                    </div>
                  </template>
                  <div v-else class="content">
                    <p>There are no reports added to this dashboard yet.</p>
                    <router-link
                      class="button is-interactive-primary is-outlined"
                      :to="{ name: 'analyze' }"
                      >Analyze Some Data First</router-link
                    >
                  </div>
                </template>
              </template>

              <template v-else>
                <div class="column content">
                  <p>
                    Select a dashboard or click "New" to the left and add
                    reports to it to view them here.
                  </p>
                  <p>You can add a report by:</p>
                  <ul>
                    <li>
                      In Analyze, clicking "Add to Dashboard" after creating a
                      report
                    </li>
                    <li>
                      Clicking the "Add Report" button to an existing dashboard
                      (coming soon)
                    </li>
                  </ul>
                </div>
              </template>

              <NewDashboardModal
                v-if="isNewDashboardModalOpen"
                @close="toggleNewDashboardModal"
              />
            </div>
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
