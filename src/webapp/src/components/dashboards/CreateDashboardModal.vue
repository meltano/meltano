<script>
import Vue from 'vue'

export default {
  name: 'CreateDashboardModal',
  props: {
    dashboard: { type: Object, default: null },
    report: { type: Object, default: null }
  },
  data() {
    return {
      saveDashboardSettings: { name: null, description: null }
    }
  },
  computed: {
    getHeaderLabel() {
      return `${this.getIsEditing ? 'Edit' : 'Create'} Dashboard`
    },
    getIsAddingToReport() {
      return this.report !== null
    },
    getIsEditing() {
      return this.dashboard !== null
    }
  },
  created() {
    this.saveDashboardSettings.name = this.dashboard
      ? this.dashboard.name
      : `dashboard-${new Date().getTime()}`
    this.saveDashboardSettings.description = this.dashboard
      ? this.dashboard.description
      : null
  },
  methods: {
    close() {
      this.$emit('close')
    },
    saveDashboard() {
      let action = null
      if (this.getIsAddingToReport) {
        action = this.$store.dispatch('dashboards/saveNewDashboardWithReport', {
          data: this.saveDashboardSettings,
          report: this.report
        })
      } else if (this.getIsEditing) {
        action = this.$store.dispatch('dashboards/updateDashboard', {
          dashboard: this.dashboard,
          newSettings: this.saveDashboardSettings
        })
      } else {
        action = this.$store.dispatch(
          'dashboards/saveDashboard',
          this.saveDashboardSettings
        )
      }

      const dashboardName = this.saveDashboardSettings.name
      action
        .then(() => {
          Vue.toasted.global.success(`Dashboard Saved - ${dashboardName}`)
        })
        .catch(this.$error.handle)
        .finally(this.close)
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{ getHeaderLabel }}</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <div>
          <div class="field">
            <label class="label">Name</label>
            <div class="control">
              <input
                v-model="saveDashboardSettings.name"
                class="input"
                type="text"
                placeholder="Name your dashboard"
                @focus="$event.target.select()"
              />
            </div>
          </div>
          <div class="field">
            <label class="label">Description</label>
            <div class="control">
              <textarea
                v-model="saveDashboardSettings.description"
                class="textarea"
                placeholder="Describe your dashboard for easier reference later"
                @focus="$event.target.select()"
              ></textarea>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          data-test-id="button-create-dashboard"
          class="button is-interactive-primary"
          :disabled="!saveDashboardSettings.name"
          @click="saveDashboard"
        >
          Save
        </button>
      </footer>
    </div>
  </div>
</template>

<style></style>
