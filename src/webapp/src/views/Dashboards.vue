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
      this.getActiveDashboardReportsWithQueryResults()
    }
  },
  created() {
    this.initialize(this.$route.params.slug)
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'setDashboard',
      'getActiveDashboardReportsWithQueryResults'
    ]),
    toggleNewDashboardModal() {
      this.isNewDashboardModalOpen = !this.isNewDashboardModalOpen
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class="is-marginless">Dashboards</h1>
        </div>
      </div>
    </div>

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

              <template v-if="dashboards.length > 0">
                <div class="panel">
                  <a
                    v-for="dashboard in dashboards"
                    :key="dashboard.id"
                    class="panel-block space-between has-text-weight-medium"
                    :class="{ 'is-active': isActive(dashboard) }"
                    @click="setDashboard(dashboard)"
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

                <div
                  v-for="report in activeDashboardReports"
                  :key="report.id"
                  class="content"
                >
                  <h5 class="has-text-centered">{{ report.name }}</h5>
                  <chart
                    :chart-type="report.chartType"
                    :results="report.queryResults"
                    :result-aggregates="report.queryResultAggregates"
                  ></chart>
                </div>
              </template>

              <template v-else>
                <div class="column content">
                  <p>
                    Click "New" to the left and add reports to it to view them
                    here. You can add a report by:
                  </p>
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
