<template>
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
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link" @click="saveDashboard">Create</button>
      </div>
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
    saveDashboard() {
      this.$store.dispatch('dashboards/saveDashboard', this.saveDashboardSettings);
    },
  },
}
</script>

<style scoped>

</style>