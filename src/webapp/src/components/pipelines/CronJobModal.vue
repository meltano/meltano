<script>
import VueCronEditorBuefy from 'vue-cron-editor-buefy'
export default {
  name: 'CronJobModal',
  components: {
    VueCronEditorBuefy
  },
  data: () => ({
    cronExpression: '*/1 * * * *'
  }),
  methods: {
    close() {
      this.$router.push({ name: 'pipelines' })
    },
    saveInterval(expression) {
      console.log(expression)
      this.close()
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">Variable CRON job</p>
        <button aria-label="close" class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <!-- <v-app>
          <v-content> -->
        <VueCronEditorBuefy v-model="cronExpression" />
        {{ cronExpression }}
        <!-- </v-content>
        </v-app> -->
      </section>
      <footer class="modal-card-foot field is-grouped is-grouped-right">
        <button class="button" @click="close">Cancel</button>
        <div class="field has-addons">
          <div class="control">
            <button
              class="button is-interactive-primary"
              @click="saveInterval(cronExpression)"
            >
              Save
            </button>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style></style>
