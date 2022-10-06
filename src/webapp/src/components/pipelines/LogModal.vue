<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import DownloadButton from '@/components/generic/DownloadButton'
import SubscribeButton from '@/components/generic/SubscribeButton'
import orchestrationsApi from '@/api/orchestrations'
import poller from '@/utils/poller'
import utils from '@/utils/utils'

export default {
  name: 'LogModal',
  components: {
    ConnectorLogo,
    DownloadButton,
    SubscribeButton,
  },
  data() {
    return {
      hasError: false,
      hasLogExceededMaxSize: false,
      isPolling: true,
      jobLog: null,
      jobPoller: null,
      jobStatus: null,
      shouldAutoScroll: true,
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getRunningPipelinestateIds']),
    ...mapState('orchestration', ['pipelines']),
    ...mapGetters('plugins', ['getPluginLabel']),
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
    isUITrigger() {
      return this.jobStatus && this.jobStatus.trigger === 'ui'
    },
    isNotificationEnabled() {
      return !!this.$flask['isNotificationEnabled']
    },
    isAnalysisEnabled() {
      return !!this.$flask['isAnalysisEnabled']
    },
    relatedPipeline() {
      return this.pipelines.find((pipeline) => pipeline.name === this.stateId)
    },
    dataSourceLabel() {
      return this.relatedPipeline
        ? this.getPluginLabel('extractors', this.relatedPipeline.extractor)
        : ''
    },
  },
  created() {
    this.stateId = this.$route.params.stateId
    this.initJobPoller()
  },
  beforeDestroy() {
    this.jobPoller.dispose()
  },
  methods: {
    ...mapActions('orchestration', ['getJobLog']),
    close() {
      this.$router.push({ name: 'pipelines' })
    },
    scrollToLogsBottom() {
      utils.scrollToBottom(this.$refs['log-view'])
    },
    initJobPoller() {
      const pollFn = () => {
        this.getJobLog(this.stateId)
          .then((response) => {
            this.jobStatus = response.data
            this.hasError = this.jobStatus.hasError
            this.hasLogExceededMaxSize = this.jobStatus.hasLogExceededMaxSize
            this.jobLog = this.jobStatus.log
          })
          .catch((error) => {
            this.jobLog = error.response.data.code
          })
          .finally(() => {
            if (this.getRunningPipelinestateIds.indexOf(this.stateId) === -1) {
              this.isPolling = false
              this.jobPoller.dispose()
            }
            if (this.shouldAutoScroll) {
              this.scrollToLogsBottom()
            }
          })
      }
      this.jobPoller = poller.create(pollFn, null, 1000)
      this.jobPoller.init()
    },
    retry() {
      this.jobLog = null
      this.initJobPoller()
    },
    getHelp() {
      window.open('https://docs.meltano.com/the-project/community')
    },
  },
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card is-wide" :class="{ 'modal-card-log': jobLog }">
      <header class="modal-card-head">
        <figure v-if="relatedPipeline" class="media-left">
          <p class="image level-item is-24x24 container">
            <ConnectorLogo :connector="relatedPipeline.extractor" />
          </p>
        </figure>
        <p class="modal-card-title">{{ dataSourceLabel }} Pipeline Run Log</p>
        <div
          class="tooltip is-tooltip-left"
          data-tooltip="The pipeline still runs when closed"
        >
          <button class="delete" aria-label="close" @click="close"></button>
        </div>
      </header>
      <section v-if="relatedPipeline" class="modal-card-body">
        <article class="message is-small is-info">
          <p class="message-header">
            Your data is being extracted from {{ dataSourceLabel }}.
          </p>
          <div class="message-body content">
            <p>Please note:</p>
            <ul>
              <li>
                Depending on the specific extractor, time period, and amount of
                data, extraction can take as little as a
                <em>few seconds</em>, or as long as <em>multiple hours</em>.
              </li>
              <li>
                Extraction will continue in the background even if you close
                this view.
              </li>
              <li v-if="isAnalysisEnabled">
                Once extraction is complete, you can explore the imported data
                using the "Explore" button that will appear on the bottom right
                of this view and on the Extractors page.
              </li>
            </ul>
            <p v-if="isUITrigger && isNotificationEnabled">
              <SubscribeButton
                event-type="pipeline_manual_run"
                source-type="pipeline"
                :source-id="stateId"
              >
                <label
                  slot="label"
                  class="label has-text-inherited is-small"
                  for="email"
                  >Please notify me when the data is ready</label
                >
              </SubscribeButton>
            </p>
          </div>
        </article>
      </section>
      <section
        v-if="!hasLogExceededMaxSize"
        ref="log-view"
        class="modal-card-body modal-card-body-log is-overflow-y-scroll"
      >
        <pre
          v-if="jobLog"
        ><code class="is-size-8">{{jobLog}}{{getLogAppender}}</code></pre>
        <progress v-else class="progress is-small is-info"></progress>
      </section>
      <section class="modal-card-body">
        <article v-if="hasLogExceededMaxSize" class="message is-small">
          <div class="message-body">
            <div class="content">
              <p>The log is too large to display inline. Download it below.</p>
            </div>
          </div>
        </article>
        <DownloadButton
          v-if="hasLogExceededMaxSize || !isPolling"
          label="Download Log"
          :file-name="`${stateId}-job-log.txt`"
          :trigger-promise="getDownloadPromise"
          :trigger-payload="{ stateId }"
        ></DownloadButton>
        <label v-else class="checkbox is-unselectable">
          <input v-model="shouldAutoScroll" type="checkbox" />
          Autoscroll
        </label>
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
          <button
            class="button tooltip is-tooltip-left"
            data-tooltip="The pipeline still runs when closed"
            @click="close"
          >
            Close
          </button>

          <button v-if="hasError" class="button is-danger" @click="getHelp">
            Get Help
          </button>
          <button class="button is-info" @click="retry">
            <span>Retry</span>
            <span class="icon is-small">
              <font-awesome-icon icon="redo"></font-awesome-icon>
            </span>
          </button>
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
