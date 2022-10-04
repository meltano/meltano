<script>
import { mapActions, mapState, mapGetters } from 'vuex'
import Vue from 'vue'

// Used https://github.com/karoletrych/vue-cron-editor for the CRON editor
import VueCronEditorBuefy from 'vue-cron-editor-buefy'

export default {
  name: 'CronJobModal',
  components: {
    VueCronEditorBuefy,
  },
  data() {
    return {
      isLoaded: false,
      isSaving: false,
      cronExpression: '*/1 * * * *',
    }
  },
  computed: {
    ...mapState('orchestration', ['pipelines']),
    ...mapGetters('plugins', ['getInstalledPlugin', 'getPluginLabel']),
    relatedPipeline() {
      return this.pipelines.find((pipeline) => pipeline.name === this.stateId)
    },
  },
  created() {
    this.stateId = this.$route.params.stateId
    if (
      this.$route.params.cronInterval &&
      this.$route.params.cronInterval.includes('*')
    ) {
      this.cronExpression = this.$route.params.cronInterval
    }
  },
  methods: {
    ...mapActions('orchestration', ['updatePipelineSchedule']),
    close() {
      this.$router.push({
        name: 'pipelines',
        params: { triggerPipelineRefresh: true },
      })
    },
    saveInterval(expression) {
      const pipeline = this.relatedPipeline
      this.isSaving = true
      const pluginNamespace = this.getInstalledPlugin(
        'extractors',
        pipeline.extractor
      ).namespace
      this.updatePipelineSchedule({
        interval: expression,
        pipeline,
        pluginNamespace,
      })
        .then(() => {
          Vue.toasted.global.success(
            `Pipeline successfully updated - ${this.pipeline.name}`
          )
        })
        .catch((error) => {
          Vue.toasted.global.error(error.response.data.code)
        })
        .finally(() => {
          this.isSaving = false
          this.close()
        })
    },
  },
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Variable CRON Job</p>
        <button aria-label="close" class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <p>
          This is your current CRON expression
          <code>{{ cronExpression }}</code> for
          <code>{{ relatedPipeline.name }}</code
          >.
        </p>
        <hr />
        <VueCronEditorBuefy v-model="cronExpression" />
      </section>
      <footer class="modal-card-foot field is-grouped is-grouped-right">
        <button class="button" @click="close">Cancel</button>
        <div class="field has-addons">
          <div class="control">
            <button
              class="button is-interactive-primary"
              :disabled="isSaving"
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
.enable-bulma {
  margin-bottom: 40px;
}

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

.modal-card-body ul {
  list-style: disc;
  margin-left: 17px;
}

.cron-next-ten-intervals {
  margin-bottom: 10px;
}
</style>
