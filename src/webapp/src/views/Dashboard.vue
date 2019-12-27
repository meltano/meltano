<script>
import { mapActions, mapState } from 'vuex'

import Chart from '@/components/analyze/Chart'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboard',
  components: {
    Chart,
    RouterViewLayout
  },
  data() {
    return {
      isActiveDashboardLoading: false
    }
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReports',
      'dashboards',
      'isInitializing',
      'reports'
    ]),
    dashboardEmail() {
      // eslint-disable-next-line
      return `mailto:?subject=Dashboard: ${this.activeDashboard.name}&body=${window.location}`
    },
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
    this.initialize(this.$route.params.slug)
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'getActiveDashboardReportsWithQueryResults'
    ]),
    goToDesign(report) {
      const params = {
        design: report.design,
        model: report.model,
        namespace: report.namespace
      }
      this.$router.push({ name: 'analyzeDesign', params })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <section>
        <div class="columns is-vcentered">
          <div class="column">
            <h2 class="title">{{ activeDashboard.name }}</h2>
            <h3 v-if="activeDashboard.description" class="subtitle">
              {{ activeDashboard.description }}
            </h3>
          </div>
          <div class="column">
            <div class="buttons is-pulled-right">
              <a class="button" :href="dashboardEmail">Share</a>
              <router-link class="button" :to="{ name: 'dashboards' }"
                >Back to Dashboards</router-link
              >
            </div>
          </div>
        </div>

        <div v-if="activeDashboardReports.length" class="columns is-multiline">
          <div
            v-for="report in activeDashboardReports"
            :key="report.id"
            class="column is-half"
          >
            <div class="box">
              <div class="columns is-vcentered">
                <div class="column">
                  <h3 class="title is-5 is-inline-block">{{ report.name }}</h3>
                  <div class="field is-pulled-right is-inline-block">
                    <div class="buttons">
                      <a class="button is-small" @click="goToReport(report)"
                        >Edit</a
                      >
                      <a class="button is-small" @click="goToDesign(report)"
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
          </div>
        </div>

        <progress
          v-else-if="isInitializing || isActiveDashboardLoading"
          class="progress is-small is-info"
        ></progress>

        <div v-else class="columns">
          <div class="column">
            <div class="box">
              <div class="content">
                <p>No reports yet...</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
