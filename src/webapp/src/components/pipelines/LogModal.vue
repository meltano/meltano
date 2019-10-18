<script>
import { mapActions, mapGetters } from 'vuex'

import poller from '@/utils/poller'

export default {
  name: 'LogModal',
  data() {
    return {
      isPolling: true,
      jobLog: null,
      jobPoller: null
    }
  },
  computed: {
    ...mapGetters('configuration', ['getRunningPipelineJobIds'])
  },
  created() {
    this.jobId = this.$route.params.jobId
    this.initJobPoller()
  },
  methods: {
    ...mapActions('configuration', ['getJobLog']),
    close() {
      if (this.prevRoute) {
        this.$router.go(-1)
      } else {
        this.$router.push({ name: 'schedules' })
      }
    },
    initJobPoller() {
      const pollFn = () => {
        this.getJobLog(this.jobId)
          .then(response => {
            this.jobLog = response.data.log
          })
          .catch(error => {
            this.jobLog = error.response.data.code
          })
          .finally(() => {
            if (this.getRunningPipelineJobIds.indexOf(this.jobId) === -1) {
              this.isPolling = false
              this.jobPoller.dispose()
            }
          })
      }
      this.jobPoller = poller.create(pollFn, null, 1200)
      this.jobPoller.init()
    }
  },
  beforeDestroy() {
    this.jobPoller.dispose()
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">
          Run Log: <span class="is-family-code">{{ jobId }}</span>
        </p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <div class="content">
          <div v-if="jobLog">
            <pre><code>{{jobLog}}{{isPolling ? '...' : ''}}</code></pre>
          </div>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Close</button>
        <button
          class="button is-interactive-primary"
          :class="{ 'is-loading': isPolling }"
          :disabled="isPolling"
        >
          Analyze
        </button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
