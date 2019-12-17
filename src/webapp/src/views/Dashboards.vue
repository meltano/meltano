<script>
import { mapActions, mapState } from 'vuex'
import Chart from '@/components/analyze/Chart'
import Dropdown from '@/components/generic/Dropdown'
import NewDashboardModal from '@/components/dashboards/NewDashboardModal'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboards',
  components: {
    Chart,
    Dropdown,
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
    deleteDashboard(dashboard) {
      console.log('delete', dashboard)
    },
    goToDashboard(dashboard) {
      this.updateCurrentDashboard(dashboard).then(() => {
        this.$router.push({ name: 'dashboard', params: dashboard })
      })
    },
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
        <div class="columns is-vcentered">
          <div class="column">
            <h2 class="title is-inline-block">Dashboards</h2>
            <div class="field is-pulled-right is-inline-block">
              <div class="control">
                <button
                  class="button is-medium is-interactive-primary"
                  @click="toggleNewDashboardModal"
                >
                  <span>Create</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="dashboards.length > 0" class="box">
          <table class="table is-fullwidth is-narrow is-hoverable is-size-7	">
            <thead>
              <tr>
                <th>
                  <span>Name</span>
                  <span
                    class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-right"
                    data-tooltip="The unique identifier for an ELT pipeline schedule and its settings."
                  >
                    <font-awesome-icon icon="info-circle"></font-awesome-icon>
                  </span>
                </th>
                <th>
                  <span>Description</span>
                  <span
                    class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-bottom"
                    data-tooltip="The connector for data extraction within a scheduled ELT pipeline."
                  >
                    <font-awesome-icon icon="info-circle"></font-awesome-icon>
                  </span>
                </th>
                <th class="has-text-right">
                  <span>Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <template v-for="dashboard in dashboards">
                <tr
                  :key="dashboard.id"
                  data-test-id="dashboard-link"
                  :class="{ 'is-active': isActive(dashboard) }"
                  @click="goToDashboard(dashboard)"
                >
                  <td>
                    <p>{{ dashboard.name }}</p>
                  </td>
                  <td>
                    <p>{{ dashboard.description }}</p>
                  </td>
                  <td>
                    <div class="buttons is-right">
                      <a class="button is-small">Edit</a>
                      <Dropdown
                        :button-classes="
                          `is-small is-danger is-outlined ${
                            false ? 'is-loading' : ''
                          }`
                        "
                        :disabled="false"
                        :tooltip="{
                          classes: 'is-tooltip-left',
                          message: 'Delete this dashboard'
                        }"
                        menu-classes="dropdown-menu-300"
                        icon-open="trash-alt"
                        icon-close="caret-up"
                        is-right-aligned
                      >
                        <div class="dropdown-content is-unselectable">
                          <div class="dropdown-item">
                            <div class="content">
                              <p>
                                Please confirm deletion of dashboard:<br /><em
                                  >{{ dashboard.name }}</em
                                >.
                              </p>
                            </div>
                            <div class="buttons is-right">
                              <button
                                class="button is-text"
                                data-dropdown-auto-close
                              >
                                Cancel
                              </button>
                              <button
                                class="button is-danger"
                                data-dropdown-auto-close
                                @click="deleteDashboard(dashboard)"
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        </div>
                      </Dropdown>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <progress
          v-else-if="isInitializing"
          class="progress is-small is-info"
        ></progress>
        <div v-else>
          <div class="content">
            <p>No dashboards...</p>
          </div>
        </div>
      </section>

      <NewDashboardModal
        v-if="isNewDashboardModalOpen"
        @close="toggleNewDashboardModal"
      />
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
