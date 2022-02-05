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
      console.log(`i am at this pipeline: ${this.pipeline.name}`)
      this.close()
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Variable CRON job</p>
        <button aria-label="close" class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <VueCronEditorBuefy v-model="cronExpression" />
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

<style lang="scss">
.enable-bulma .tabs li.is-active a {
  color: #464acb;
}
.enable-bulma .centered-checkbox-group {
  width: 62%;
}

.enable-bulma .card {
  box-shadow: none;
  display: flex;
  justify-content: center;
}
</style>
