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
      <footer class="modal-card-foot is-pull-right">
        <button class="button" @click="close">Cancel</button>
        <button class="button is-success" @click="saveDashboard">Create</button>
      </footer>
    </div>
  </div>

</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'CreateDashboard',
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
      this.$store.dispatch('dashboards/saveDashboard', this.saveDashboardSettings);
      this.close();
    },
  },
}
</script>

<style scoped>

</style>