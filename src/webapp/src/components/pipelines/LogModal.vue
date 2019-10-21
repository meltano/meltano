<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import capitalize from '@/filters/capitalize'
import Dropdown from '@/components/generic/Dropdown'
import poller from '@/utils/poller'
import underscoreToSpace from '@/filters/underscoreToSpace'
import utils from '@/utils/utils'

export default {
  name: 'LogModal',
  components: {
    Dropdown
  },
  filters: {
    capitalize,
    underscoreToSpace
  },
  data() {
    return {
      hasError: false,
      isPolling: true,
      jobLog: null,
      jobPoller: null
    }
  },
  computed: {
    ...mapGetters('configuration', ['getRunningPipelineJobIds']),
    ...mapGetters('repos', ['hasModels', 'urlForModelDesign']),
    ...mapState('repos', ['models'])
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
            this.hasError = response.data.hasError
          })
          .catch(error => {
            this.jobLog = error.response.data.code
          })
          .finally(() => {
            if (this.getRunningPipelineJobIds.indexOf(this.jobId) === -1) {
              this.isPolling = false
              this.jobPoller.dispose()
            }
            utils.scrollToBottom(this.$refs['log-view'])
          })
      }
      this.jobPoller = poller.create(pollFn, null, 1200)
      this.jobPoller.init()
    },
    submitIssue() {
      window.open(
        'https://gitlab.com/meltano/meltano/issues/new?issue%5Bassignee_id%5D=&issue%5Bmilestone_id%5D=&issuable_template=bugs'
      )
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
      <section ref="log-view" class="modal-card-body is-overflow-y-scroll">
        <div class="content">
          <div v-if="jobLog">
            <pre><code>{{jobLog}}{{isPolling ? '...' : ''}}</code></pre>
          </div>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
      </section>
      <footer class="modal-card-foot buttons is-right">
        <button class="button" @click="close">Close</button>

        <button v-if="hasError" class="button is-danger" @click="submitIssue">
          Submit Issue
        </button>
        <Dropdown
          v-else
          label="Analyze"
          :disabled="isPolling"
          :button-classes="
            `is-interactive-primary ${isPolling ? 'is-loading' : ''}`
          "
          :menu-classes="'dropdown-menu-300'"
          icon-open="chart-line"
          icon-close="caret-down"
          is-right-aligned
          is-up
        >
          <div class="dropdown-content is-unselectable">
            <div
              v-for="(v, model) in models"
              :key="`${model}-panel`"
              class="box box-analyze-nav is-borderless is-shadowless is-marginless"
            >
              <div class="content">
                <h3 class="is-size-6">
                  {{ v.name | capitalize | underscoreToSpace }}
                </h3>
                <h4 class="is-size-7 has-text-grey">
                  {{ v.namespace }}
                </h4>
              </div>
              <div class="buttons">
                <router-link
                  v-for="design in v['designs']"
                  :key="design"
                  class="button is-small is-interactive-primary is-outlined"
                  :to="urlForModelDesign(model, design)"
                  >{{ design | capitalize | underscoreToSpace }}</router-link
                >
              </div>
            </div>
          </div>
        </Dropdown>
      </footer>
    </div>
  </div>
</template>

<style lang="scss"></style>
