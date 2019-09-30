<script>
import { mapActions } from 'vuex'

export default {
  name: 'LogModal',
  data() {
    return {
      jobLog: '',
      isRefreshing: false
    }
  },
  created() {
    this.jobIdFromRoute = this.$route.params.jobId
    this.updateJobLog()
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
    refresh() {
      this.isRefreshing = true
      this.updateJobLog()
    },
    updateJobLog() {
      this.getJobLog(this.jobIdFromRoute)
        .then(response => (this.jobLog = response.data.log))
        .catch(error => {
          this.jobLog = error.response.data.code
        })
        .finally(() => (this.isRefreshing = false))
    }
  }
}
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">
          Run Log: <span class="is-family-code">{{ jobIdFromRoute }}</span>
        </p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section class="modal-card-body is-overflow-y-scroll">
        <div class="content">
          <div v-if="jobLog">
            <pre><code>{{jobLog}}</code></pre>
            <button
              class="button"
              :class="{ 'is-loading': isRefreshing }"
              aria-label="refresh"
              @click="refresh"
            >
              Refresh
            </button>
          </div>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Close</button>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
