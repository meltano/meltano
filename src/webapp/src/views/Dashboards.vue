<script>
import Vue from 'vue'
import { mapActions, mapState } from 'vuex'

import Dropdown from '@/components/generic/Dropdown'
import CreateDashboardModal from '@/components/dashboards/CreateDashboardModal'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Dashboards',
  components: {
    Dropdown,
    CreateDashboardModal,
    RouterViewLayout
  },
  data() {
    return {
      isCreateDashboardModalOpen: false,
      dashboardInFocus: null
    }
  },
  computed: {
    ...mapState('dashboards', ['dashboards', 'isInitializing'])
  },
  created() {
    this.initialize()
  },
  methods: {
    ...mapActions('dashboards', [
      'deleteDashboard',
      'initialize',
      'updateCurrentDashboard'
    ]),
    closeCreateDashboardModal() {
      this.isCreateDashboardModalOpen = false
      this.dashboardInFocus = null
    },
    editDashboard(dashboard) {
      this.dashboardInFocus = dashboard
      this.openCreateDashboardModal()
    },
    goToDashboard(dashboard) {
      this.updateCurrentDashboard(dashboard).then(() => {
        this.$router.push({ name: 'dashboard', params: dashboard })
      })
    },
    openCreateDashboardModal() {
      this.isCreateDashboardModalOpen = open
    },
    removeDashboard(dashboard) {
      this.deleteDashboard(dashboard)
        .then(() =>
          Vue.toasted.global.success(
            `Dashboard Successfully Removed - ${dashboard.name}`
          )
        )
        .catch(err => {
          this.$error.handle(err)
          this.closeCreateDashboardModal()
        })
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
                  @click="openCreateDashboardModal"
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
                <th>
                  <span>Report Count</span>
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
                    <p>{{ dashboard.reportIds.length }}</p>
                  </td>
                  <td>
                    <div class="buttons is-right">
                      <a
                        class="button is-small is-interactive-primary is-outlined"
                        @click.stop="goToDashboard(dashboard)"
                        >View</a
                      >
                      <a
                        class="button is-small"
                        @click.stop="editDashboard(dashboard)"
                        >Edit</a
                      >
                      <Dropdown
                        :button-classes="
                          `is-small is-danger is-outlined ${
                            dashboard.isDeleting ? 'is-loading' : ''
                          }`
                        "
                        :disabled="dashboard.isDeleting"
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
                                @click="removeDashboard(dashboard)"
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

      <CreateDashboardModal
        v-if="isCreateDashboardModalOpen"
        :dashboard="dashboardInFocus"
        @close="closeCreateDashboardModal"
      />
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
