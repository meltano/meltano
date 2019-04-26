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
              <input class="input"
                      type="text"
                      placeholder="Name your dashboard"
                      v-model="saveDashboardSettings.name">
            </div>
          </div>
          <div class="field">
            <label class="label">Description</label>
            <div class="control">
              <textarea class="textarea"
                        placeholder="Describe your dashboard for easier reference later"
                        v-model="saveDashboardSettings.description"></textarea>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button" @click="close">Cancel</button>
        <button
          class="button is-interactive-primary"
          :disabled="!saveDashboardSettings.name"
          @click="saveDashboard">Create</button>
      </footer>
    </div>
  </div>

</template>

<script>
export default {
  name: 'NewDashboardModal',
  data() {
    return {
      saveDashboardSettings: { name: null, description: null },
    };
  },
  methods: {
    close() {
      this.$emit('close');
    },
    saveDashboard() {
      if (this.report) {
        this.$store.dispatch('dashboards/saveNewDashboardWithReport', {
          data: this.saveDashboardSettings,
          report: this.report,
        });
      } else {
        this.$store.dispatch('dashboards/saveDashboard', this.saveDashboardSettings);
      }
      this.close();
    },
  },
  props: {
    report: Object,
  },
};
</script>

<style scoped>

.modal-card-foot {
  justify-content: flex-end;
}

</style>
