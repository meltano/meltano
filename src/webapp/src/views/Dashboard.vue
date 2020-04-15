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
      editableReports: [],
      isEditing: false,
      reportsChanged: false
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
      return this.isEditing || this.reportsChanged
        ? this.editableReports
        : this.activeDashboardReportsWithQueryResults
    }
  },
  watch: {
    isEditing() {
      if (this.isEditing) {
        this.editableReports = []

        this.activeDashboardReportsWithQueryResults.forEach(report => {
          this.editableReports.push(report)
        })
      }
    }
  },
  beforeDestroy() {
    this.$store.dispatch('dashboards/resetActiveDashboard')
    this.$store.dispatch('dashboards/resetActiveDashboardReports')
  },
  created() {
    this.initialize(this.$route.params.slug).catch(this.$error.handle)
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
    updateDashboardReportIndexes() {
      if (this.reportsChanged) {
        this.updateDashboard({
          dashboard: this.activeDashboard,
          newSettings: {
            ...this.activeDashboard,
            reportIds: this.editableReports.map(report => report.id)
          }
        })
          .then(() => {
            this.updateActiveDashboardReportsWithQueryResults(
              this.editableReports
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

      this.isEditing = !this.isEditing
    },
    updateReportIndex({ oldIndex, newIndex }) {
      const report = this.editableReports[oldIndex]
      this.editableReports.splice(oldIndex, 1)
      this.editableReports.splice(newIndex, 0, report)
      this.reportsChanged = true
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
            <div v-if="isEditing" class="buttons is-right">
              <button class="button" @click="updateDashboardReportIndexes">
                Save
              </button>
              <button class="button" @click="isEditing = !isEditing">
                Cancel
              </button>
            </div>
            <div v-else class="buttons is-pulled-right">
              <button
                v-if="!isEditing"
                class="button"
                @click="isEditing = !isEditing"
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
            :is-editing="isEditing"
            @update-report-index="updateReportIndex"
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
