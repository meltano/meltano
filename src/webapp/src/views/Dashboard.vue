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
      editableDashboardReports: [],
      isActiveDashboardLoading: false,
      isEditable: false,
      isUpdated: false
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
      return this.isEditable || this.isUpdated
        ? this.editableDashboardReports
        : this.activeDashboardReports
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
    isEditable() {
      if (this.isEditable) {
        this.editableDashboardReports = []

        this.activeDashboardReports.forEach(report => {
          this.editableDashboardReports.push(report)
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
      'updateActiveDashboardReports',
      'updateDashboard'
    ]),
    updateReportPosition({ isUpdated, oldPosition, newPosition }) {
      const report = this.editableDashboardReports[oldPosition]
      this.editableDashboardReports.splice(oldPosition, 1)
      this.editableDashboardReports.splice(newPosition, 0, report)
      this.isUpdated = isUpdated
    },
    updateDashboardReportPositions() {
      if (this.isUpdated) {
        this.updateDashboard({
          dashboard: this.activeDashboard,
          newSettings: {
            ...this.activeDashboard,
            reportIds: this.editableDashboardReports.map(report => {
              return report.id
            })
          }
        })
          .then(() => {
            this.updateActiveDashboardReports(this.editableDashboardReports)
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

      this.isEditable = !this.isEditable
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
            <div v-if="isEditable" class="buttons is-pulled-right">
              <button class="button" @click="updateDashboardReportPositions">
                Save
              </button>
              <button class="button" @click="isEditable = !isEditable">
                Cancel
              </button>
            </div>
            <div v-else class="buttons is-pulled-right">
              <a class="button" :href="dashboardEmail">Share</a>
              <button
                v-if="!isEditable"
                class="button"
                @click="isEditable = !isEditable"
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
            :edit="isEditable"
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
