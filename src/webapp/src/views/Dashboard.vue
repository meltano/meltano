<script>
import { mapActions, mapState } from 'vuex'
import Vue from 'vue'

import EmbedShareButton from '@/components/generic/EmbedShareButton'
import Report from '@/components/Report'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboard',
  components: {
    EmbedShareButton,
    Report,
    RouterViewLayout
  },
  data() {
    return {
      editableDashboardReports: [],
      isEditable: false,
      isUpdated: false
    }
  },
  computed: {
    ...mapState('dashboards', [
      'activeDashboard',
      'activeDashboardReportsWithQueryResults',
      'dashboards',
      'isInitializing',
      'isLoadingActiveDashboard',
      'reports'
    ]),
    displayedReports() {
      return this.isEditable || this.isUpdated
        ? this.editableDashboardReports
        : this.activeDashboardReportsWithQueryResults
    }
  },
  watch: {
    isEditable() {
      if (this.isEditable) {
        this.editableDashboardReports = []

        this.activeDashboardReportsWithQueryResults.forEach(report => {
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
    this.getPipelineSchedules()
  },
  methods: {
    ...mapActions('dashboards', [
      'initialize',
      'getActiveDashboardReportsWithQueryResults',
      'updateActiveDashboardReportsWithQueryResults',
      'updateDashboard'
    ]),
    ...mapActions('orchestration', ['getPipelineSchedules']),
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
            this.updateActiveDashboardReportsWithQueryResults(
              this.editableDashboardReports
            )
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
    },
    updateReportPosition({ isUpdated, oldPosition, newPosition }) {
      const report = this.editableDashboardReports[oldPosition]
      this.editableDashboardReports.splice(oldPosition, 1)
      this.editableDashboardReports.splice(newPosition, 0, report)
      this.isUpdated = isUpdated
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <section>
        <div class="columns is-vcentered">
          <div class="column">
            <h2 class="title">{{ activeDashboard.name }}</h2>
            <h3 v-if="activeDashboard.description" class="subtitle">
              {{ activeDashboard.description }}
            </h3>
          </div>
          <div class="column">
            <div v-if="isEditable" class="buttons is-right">
              <button class="button" @click="updateDashboardReportPositions">
                Save
              </button>
              <button class="button" @click="isEditable = !isEditable">
                Cancel
              </button>
            </div>
            <div v-else class="buttons is-pulled-right">
              <button
                v-if="!isEditable"
                class="button"
                @click="isEditable = !isEditable"
              >
                Edit
              </button>
              <EmbedShareButton
                :resource="activeDashboard"
                resource-type="dashboard"
              />
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

        <div v-else class="columns">
          <div class="column">
            <div class="box">
              <progress
                v-if="isInitializing || isLoadingActiveDashboard"
                class="progress is-small is-info"
              ></progress>
              <div v-else class="content">
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
