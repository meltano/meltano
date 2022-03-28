<script>
import { mapActions, mapGetters, mapState } from 'vuex'

import lodash from 'lodash'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import designApi from '@/api/design'

export default {
  name: 'Explore',
  components: {
    ConnectorLogo
  },
  data() {
    return {
      extractorName: '',
      pluginNamespace: '',
      hasLoadedDashboards: false,
      hasLoadedReports: false,
      model: '',
      namespace: '',
      topic: null
    }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin', 'getHasDefaultDashboards']),
    ...mapState('dashboards', ['dashboards']),
    ...mapState('plugins', ['installedPlugins']),
    ...mapState('reports', ['reports']),
    ...mapState('repos', ['models']),
    getDesignLabel() {
      return designName =>
        this.topic
          ? this.topic.designs.find(design => design.name === designName).label
          : ''
    },
    getFilteredDashboards() {
      const filteredReportIds = this.getFilteredReports.map(report => report.id)
      return this.dashboards.filter(dashboard => {
        const intersections = lodash.intersection(
          dashboard.reportIds,
          filteredReportIds
        )
        return intersections.length
      })
    },
    getFilteredReports() {
      return this.reports.filter(report => report.namespace === this.namespace)
    },
    getTitle() {
      return this.topic ? this.topic.label : ''
    },
    hasDefaultDashboards() {
      return this.getHasDefaultDashboards(this.pluginNamespace)
    }
  },
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.reinitialize()
    })
  },
  beforeRouteUpdate(to, from, next) {
    next()

    // it is crucial to wait after `next` is called so
    // the route parameters are updated.
    this.reinitialize()
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards']),
    ...mapActions('plugins', ['getInstalledPlugins']),
    ...mapActions('reports', ['getReports']),
    ...mapActions('repos', ['getModels']),
    goToDashboard(dashboard) {
      this.$router.push({ name: 'dashboard', params: dashboard })
    },
    goToDesign(design) {
      const params = {
        design: design.name,
        model: this.model,
        namespace: this.namespace
      }
      this.$router.push({
        name: 'design',
        params
      })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    },
    reinitialize() {
      // Reset flags
      this.hasLoadedDashboards = false
      this.hasLoadedReports = false
      this.pluginNamespace = ''
      this.namespace = ''
      this.model = ''
      this.topic = null

      this.extractorName = this.$route.params.extractor

      // Initialize
      this.getInstalledPlugins().then(() => {
        const extractor = this.getInstalledPlugin(
          'extractors',
          this.extractorName
        )
        this.pluginNamespace = extractor.namespace

        this.getModels()
          .then(() => {
            for (let modelKey in this.models) {
              const modelSpec = this.models[modelKey]
              if (modelSpec.plugin_namespace === this.pluginNamespace) {
                this.namespace = modelSpec.namespace
                this.model = modelSpec.name
                break
              }
            }
          })
          .then(() => designApi.getTopic(this.namespace, this.model))
          .then(response => (this.topic = response.data))
          .catch(this.$error.handle)

        this.getDashboards()
          .then(() => (this.hasLoadedDashboards = true))
          .catch(this.$error.handle)
        this.getReports()
          .then(() => (this.hasLoadedReports = true))
          .catch(this.$error.handle)
      })
    }
  }
}
</script>

<template>
  <div>
    <h2 id="explore" class="title is-flex is-vcentered">
      <div class="media is-paddingless">
        <figure class="media-left">
          <div class="image level-item is-48x48">
            <ConnectorLogo v-if="extractorName" :connector="extractorName" />
          </div>
        </figure>
      </div>
      <span>Explore {{ getTitle }}</span>
    </h2>

    <div class="columns">
      <!-- Dashboards -->
      <div class="column">
        <div class="content">
          <h3 id="dashboards" class="title">Dashboards</h3>
          <p class="subtitle">Report collections</p>
        </div>
        <div class="box">
          <progress
            v-if="!hasLoadedDashboards"
            class="progress is-small is-info"
          ></progress>
          <template v-else-if="dashboards.length">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="dashboard in getFilteredDashboards"
                :key="dashboard.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToDashboard(dashboard)"
              >
                <div>
                  <strong>{{ dashboard.name }}</strong>
                  <template v-if="dashboard.description">
                    <br />
                    <small>{{ dashboard.description }}</small>
                  </template>
                  <template v-if="dashboard.reportIds">
                    <br />
                    <small class="is-italic has-text-grey"
                      >{{ dashboard.reportIds.length }} Reports</small
                    >
                  </template>
                </div>
                <div>
                  <button
                    class="button is-interactive-primary is-pulled-right ml-05r"
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No dashboards</p></div>
          </template>
        </div>
      </div>

      <!-- Reports -->
      <div class="column">
        <div class="content">
          <h3 id="reports" class="title">Reports</h3>
          <p class="subtitle">Saved analysis</p>
        </div>
        <div class="box">
          <progress
            v-if="!hasLoadedReports"
            class="progress is-small is-info"
          ></progress>
          <template v-else-if="reports.length">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="report in getFilteredReports"
                :key="report.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToReport(report)"
              >
                <div>
                  <strong>{{ report.name }}</strong>
                  <br />
                  <small class="is-italic has-text-grey">{{
                    getDesignLabel(report.design)
                  }}</small>
                </div>
                <div>
                  <button class="button is-small is-pulled-right ml-05r">
                    View
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No reports</p></div>
          </template>
        </div>

        <p v-if="hasDefaultDashboards" class="has-text-centered is-italic">
          If the report you're looking for is not yet included with Meltano by
          default, please
          <a href="https://docs.meltano.com/the-project/community">let us know</a>!
        </p>
      </div>

      <!-- Report Builder -->
      <div class="column">
        <div class="content">
          <h3 id="report-builder" class="title">Report Builder</h3>
          <p class="subtitle">Analysis starters</p>
        </div>
        <div class="box">
          <progress v-if="!topic" class="progress is-small is-info"></progress>
          <template v-else-if="topic.designs">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="design in topic.designs"
                :key="design.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToDesign(design)"
              >
                <div>
                  <strong>{{ design.label }}</strong>
                  <template
                    v-if="
                      design.description &&
                        design.description.length &&
                        design.description != design.label
                    "
                  >
                    <br />
                    <small>{{ design.description }}</small>
                  </template>
                </div>
                <div>
                  <button class="button is-small is-pulled-right ml-05r">
                    <span>Analyze</span>
                    <span class="icon is-small">
                      <font-awesome-icon icon="chart-line"></font-awesome-icon>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No report templates</p></div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
