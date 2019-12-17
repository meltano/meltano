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
      isInitializing: false,
      isNewDashboardModalOpen: false
    }
  },
  computed: {
<<<<<<< HEAD
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
=======
    ...mapState('dashboards', ['dashboards'])
>>>>>>> further markup cleanup and properly ensure reports are using basic two-column grid with multiline until we implement a more robust resizing approach
  },
  created() {
    this.isInitializing = true
    this.initialize(this.$route.params.slug).then(() => {
      this.isInitializing = false
    })
  },
  methods: {
    ...mapActions('dashboards', ['initialize', 'updateCurrentDashboard']),
    deleteDashboard(dashboard) {
      // Todo
    },
    goToDashboard(dashboard) {
      this.updateCurrentDashboard(dashboard).then(() => {
        this.$router.push({ name: 'dashboard', params: dashboard })
      })
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
                </th>
                <th>
                  <span>Description</span>
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
                  class="has-cursor-pointer"
                  @click="goToDashboard(dashboard)"
                >
                  <td>
                    <p>{{ dashboard.name }}</p>
                  </td>
                  <td>
                    <p v-if="dashboard.description">
                      {{ dashboard.description }}
                    </p>
                    <p v-else class="is-italic has-text-grey">None</p>
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
