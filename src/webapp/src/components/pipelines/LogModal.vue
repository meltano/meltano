<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import AnalyzeList from '@/components/analyze/AnalyzeList'
import DownloadButton from '@/components/generic/DownloadButton'
import Dropdown from '@/components/generic/Dropdown'
import orchestrationsApi from '@/api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

export default {
  name: 'LogModal',
  components: {
    AnalyzeList,
    Dropdown,
    DownloadButton
  },
  data() {
    return {
      hasError: false,
      hasLogExceededMaxSize: false,
      isPolling: true,
      jobLog: null,
      jobPoller: null,
      jobStatus: null
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getRunningPipelineJobIds']),
    ...mapState('orchestration', ['pipelines']),
    getDownloadPromise() {
      return orchestrationsApi.downloadJobLog
    },
    getElapsedLabel() {
      if (!this.jobStatus) {
        return '...'
      }
      const startDate = new Date(this.jobStatus.startedAt)
      const endDate = this.jobStatus.endedAt
        ? new Date(this.jobStatus.endedAt)
        : Date.now()
      return utils.momentHumanizedDuration(startDate, endDate)
    },
    getEndedAtLabel() {
      const fallback =
        this.jobStatus && !this.jobStatus.endedAt ? 'Running...' : '...'
      return this.jobStatus && this.jobStatus.endedAt
        ? utils.momentFormatlll(this.jobStatus.endedAt)
        : fallback
    },
    getLogAppender() {
      const note = this.hasLogExceededMaxSize
        ? 'Logging stream limit hit. Use the "Download Log" button below once extraction completes.'
        : ''
      return this.isPolling ? `... ${note}` : ''
    },
    getStartedAtLabel() {
      return this.jobStatus
        ? utils.momentFormatlll(this.jobStatus.startedAt)
        : '...'
    },
    relatedPipeline() {
      return this.pipelines.find(pipeline => pipeline.name === this.jobId)
    }
  },
  created() {
    this.jobId = this.$route.params.jobId
    this.initJobPoller()
  },
  beforeDestroy() {
    this.jobPoller.dispose()
  },
  methods: {
    ...mapActions('orchestration', ['getJobLog']),
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
            this.jobStatus = response.data
            this.hasError = this.jobStatus.hasError
            if (this.jobStatus.hasLogExceededMaxSize) {
              this.hasLogExceededMaxSize = this.jobStatus.hasLogExceededMaxSize
            } else {
              this.jobLog = this.jobStatus.log
            }
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
      this.jobPoller = poller.create(pollFn, null, 1000)
      this.jobPoller.init()
    },
    getHelp() {
      window.open('https://meltano.com/docs/getting-help.html')
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide" :class="{ 'modal-card-log': jobLog }">
      <header class="modal-card-head">
        <p class="modal-card-title">
          Run Log: <span class="is-family-code">{{ jobId }}</span>
        </p>
        <button class="delete" aria-label="close" @click="close"></button>
      </header>
      <section v-if="relatedPipeline" class="modal-card-body">
        <article class="message is-small is-info">
          <div class="message-body">
            <div class="content">
              <p>
                This pipeline uses the
                <code>{{ relatedPipeline.extractor }}</code> extractor. Please
                note:
              </p>
              <ul>
                <li>
                  Depending on the specific data source, time period, and amount
                  of data, extraction can take as little as a
                  <em>few seconds</em>, or as long as <em>multiple hours</em>.
                </li>
                <li>
                  Extraction will continue in the background even if you close
                  this view.
                </li>
                <li>
                  Once extraction is complete, use the "Analyze" button (lower
                  right of this view) to analyze the imported data.
                </li>
              </ul>
            </div>
          </div>
        </article>
      </section>
      <section
        v-if="!hasLogExceededMaxSize"
        ref="log-view"
        class="modal-card-body modal-card-body-log is-overflow-y-scroll"
      >
        <pre v-if="jobLog"><code>{{jobLog}}{{getLogAppender}}</code></pre>
        <progress v-else class="progress is-small is-info"></progress>
      </section>
      <section class="modal-card-body">
        <article v-if="hasLogExceededMaxSize" class="message is-small">
          <div class="message-body">
            <div class="content">
              <p>
                The log is too large to display inline. Download it below.
              </p>
            </div>
          </div>
        </article>
        <DownloadButton
          label="Download Log"
          :file-name="`${jobId}-job-log.txt`"
          :is-disabled="isPolling"
          :trigger-promise="getDownloadPromise"
          :trigger-payload="{ jobId }"
        ></DownloadButton>
      </section>
      <footer class="modal-card-foot h-space-between">
        <div class="field is-grouped is-grouped-multiline">
          <div class="control control-job-log-tags">
            <div class="tags has-addons">
              <span class="tag is-white">Started</span>
              <span class="tag is-info">{{ getStartedAtLabel }}</span>
            </div>
          </div>

          <div class="control control-job-log-tags">
            <div class="tags has-addons">
              <span class="tag is-white">Ended</span>
              <span class="tag is-info">{{ getEndedAtLabel }}</span>
            </div>
          </div>

          <div class="control control-job-log-tags">
            <div class="tags has-addons">
              <span class="tag is-white">Elapsed</span>
              <span class="tag is-info">{{ getElapsedLabel }}</span>
            </div>
          </div>
        </div>
        <div class="buttons is-right">
          <button class="button" @click="close">Close</button>

          <button v-if="hasError" class="button is-danger" @click="getHelp">
            Get Help
          </button>
          <Dropdown
            v-else
            label="Analyze"
            :disabled="isPolling"
            :button-classes="
              `is-interactive-primary ${isPolling ? 'is-loading' : ''}`
            "
            menu-classes="dropdown-menu-300"
            icon-open="chart-line"
            icon-close="caret-down"
            is-right-aligned
            is-up
          >
            <div class="dropdown-content is-unselectable">
              <AnalyzeList :pipeline="relatedPipeline" />
            </div>
          </Dropdown>
        </div>
      </footer>
    </div>
  </div>
</template>

<style lang="scss">
.field.is-grouped.is-grouped-multiline > .control.control-job-log-tags {
  @media screen and (min-width: $desktop) {
    margin-bottom: 0;
  }
}

.modal-card-body-log {
  height: 100%;
}

.modal-card.modal-card-log {
  height: 90vh;
}
</style>
