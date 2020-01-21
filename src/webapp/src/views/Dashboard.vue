<script>
import Vue from 'vue'
import { mapActions, mapState } from 'vuex'

import Report from '@/components/Report'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboard',
  components: {
    Report,
    RouterViewLayout
  },
  data() {
    return {
      isActiveDashboardLoading: false,
      reportLayoutWireframe: [],
      showRearrangeUi: false,
      changeHasBeenMade: false
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
    displayedReports() {
      if (this.showRearrangeUi || this.changeHasBeenMade) {
        return this.reportLayoutWireframe
      } else {
        return this.activeDashboardReports
      }
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
    },
    showRearrangeUi() {
      if (this.showRearrangeUi) {
        this.reportLayoutWireframe = []

        this.activeDashboardReports.forEach(report => {
          this.reportLayoutWireframe.push(report)
        })
      }
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
      'getActiveDashboardReportsWithQueryResults',
      'updateDashboard'
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
    },
    updateReportPosition(data) {
      const report = this.reportLayoutWireframe[data.oldPosition]
      this.reportLayoutWireframe.splice(data.oldPosition, 1)
      this.reportLayoutWireframe.splice(data.newPosition, 0, report)
      this.changeHasBeenMade = data.changeHasBeenMade
    },
    updateDashboardReportPositions() {
      if (this.changeHasBeenMade) {
        this.updateDashboard({
          dashboard: this.activeDashboard,
          newSettings: {
            ...this.activeDashboard,
            reportIds: this.reportLayoutWireframe.map(report => {
              return report.id
            })
          }
        })
          .then(() => {
            Vue.toasted.global.success(
              `Dashboard reports order successfully saved!`
            )
          })
          .catch(error => {
            Vue.toasted.global.error(
              `Dashboard reports order did not save correctly - ${error}`
            )
          })
      }

      this.showRearrangeUi = !this.showRearrangeUi
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
            <div v-if="showRearrangeUi" class="buttons is-pulled-right">
              <button class="button" @click="updateDashboardReportPositions">
                Save
              </button>
              <button
                class="button"
                @click="showRearrangeUi = !showRearrangeUi"
              >
                Cancel
              </button>
            </div>
            <div v-else class="buttons is-pulled-right">
              <a class="button" :href="dashboardEmail">Share</a>
              <button
                v-if="!showRearrangeUi"
                class="button"
                @click="showRearrangeUi = !showRearrangeUi"
              >
                Edit
              </button>
              <router-link class="button" :to="{ name: 'dashboards' }"
                >Back to Dashboards</router-link
              >
            </div>
          </div>
        </div>

        <div v-if="displayedReports.length" class="columns is-multiline">
          <Report
            v-for="(report, index) in displayedReports"
            :key="`${report.id}-${index}`"
            :report="report"
            :index="index"
            :edit="showRearrangeUi"
            @update-report-position="updateReportPosition"
          />
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
