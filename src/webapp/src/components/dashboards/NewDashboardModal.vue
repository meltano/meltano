<script>
import Vue from 'vue'

export default {
  name: 'NewDashboardModal',
  props: {
    report: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      saveDashboardSettings: { name: null, description: null }
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    saveDashboard() {
      let action = null
      if (this.report) {
        action = this.$store.dispatch('dashboards/saveNewDashboardWithReport', {
          data: this.saveDashboardSettings,
          report: this.report
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
          this.close()
          Vue.toasted.global.success(`Dashboard Saved - ${dashboardName}`)
        })
        .catch(error => {
          Vue.toasted.global.error(error.response.data.code)
        })
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">New Dashboard</p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div>
          <div class="field">
            <label class="label">Name</label>
            <div class="control">
              <input
                v-model="saveDashboardSettings.name"
                class="input"
                type="text"
                placeholder="Name your dashboard"
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
              ></textarea>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!saveDashboardSettings.name"
          @click="saveDashboard"
        >
          Create
        </button>
      </footer>
    </div>
  </div>
</template>

<style></style>
