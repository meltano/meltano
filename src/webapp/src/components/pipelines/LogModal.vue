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
      jobPoller: null,
      jobStatus: null
    }
  },
  computed: {
    ...mapGetters('orchestration', ['getRunningPipelineJobIds']),
    ...mapGetters('plugins', ['getInstalledPlugin']),
    ...mapGetters('repos', ['hasModels', 'urlForModelDesign']),
    ...mapState('orchestration', ['pipelines']),
    ...mapState('repos', ['models']),
    contextualModels() {
      let models = this.models
      if (this.relatedPipeline) {
        // Split based on '@' profiles convention
        const extractor = this.relatedPipeline.extractor.split('@')[0]
        const namespace = this.getInstalledPlugin('extractors', extractor)
          .namespace
        const filteredModels = {}
        for (const prop in models) {
          if (models[prop].plugin_namespace === namespace) {
            filteredModels[prop] = models[prop]
          }
        }

        // Fallback to all if no match
        models =
          Object.keys(filteredModels).length === 0
            ? this.models
            : filteredModels
      }

      return models
    },
    getElapsedLabel() {
      if (!this.jobStatus) {
        return '...'
      }
      const end = this.jobStatus.endedAt
        ? new Date(this.jobStatus.endedAt)
        : Date.now()
      const elapsed = end - new Date(this.jobStatus.startedAt)
      return `${Math.floor(elapsed / 1000)} sec`
    },
    getEndedAtLabel() {
      const fallback =
        this.jobStatus && !this.jobStatus.endedAt ? 'Running...' : '...'
      return this.jobStatus && this.jobStatus.endedAt
        ? utils.momentFormatlll(this.jobStatus.endedAt)
        : fallback
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
            this.jobLog = response.data.log
            this.hasError = response.data.hasError
            this.jobStatus = response.data
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
    getHelp() {
      window.open('https://meltano.com/docs/getting-help.html')
    },
    prepareAnalyzeLoader(model, design) {
      if (this.relatedPipeline) {
        localStorage.setItem(
          utils.concatLoaderModelDesign(model, design),
          this.relatedPipeline.loader
        )
      }
    }
  }
}
</script>

<template>
  <div class="modal is-active" @keyup.esc="close">
    <div class="modal-background" @click="close"></div>
    <div class="modal-card modal-card-log is-wide">
      <header class="modal-card-head">
        <p class="modal-card-title">
          Run Log: <span class="is-family-code">{{ jobId }}</span>
        </p>
      </header>
      <section v-if="isPolling && relatedPipeline" class="modal-card-body">
        <p>
          Your data is currently being pulled from
          {{ relatedPipeline.extractor }}. Please note that depending on the
          specific data source, time period, and amount of data, extraction can
          take as little as a few seconds, or as long as multiple hours.
        </p>
      </section>
      <section ref="log-view" class="modal-card-body is-overflow-y-scroll">
        <div class="content">
          <div v-if="jobLog">
            <pre><code>{{jobLog}}{{isPolling ? '...' : ''}}</code></pre>
          </div>
          <progress v-else class="progress is-small is-info"></progress>
        </div>
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
          <button class="button" @click="close">Back</button>

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
              <div
                v-for="(v, model) in contextualModels"
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
                    @click.native="prepareAnalyzeLoader(v.name, design)"
                    >{{ design | capitalize | underscoreToSpace }}</router-link
                  >
                </div>
              </div>
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

.modal-card.modal-card-log {
  height: 90vh;
}
</style>
