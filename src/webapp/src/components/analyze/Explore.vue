<script>
import { mapActions, mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import designApi from '@/api/design'

export default {
  name: 'Explore',
  components: {
    ConnectorLogo
  },
  data() {
    return {
      hasLoadedDashboards: false,
      hasLoadedReports: false,
      model: '',
      namespace: '',
      topic: null
    }
  },
  computed: {
    ...mapState('dashboards', ['dashboards']),
    ...mapState('reports', ['reports']),
    getExtractorName() {
      return this.topic ? `tap-${this.topic.name}` : ''
    },
    getFilteredDashboards() {
      // TODO in order for filtering to work we need to do a dashboard version/migration and provide a namespace key
      return this.dashboards //.filter(dashboard => dashboard.namespace === this.namespace)
    },
    getFilteredReports() {
      return this.reports.filter(report => report.namespace === this.namespace)
    },
    getReportTemplateAttributesCount() {
      return reportTemplate => {
        const filterer = attribute => !attribute.hidden
        const reducer = (acc, curr) =>
          acc +
          curr.columns.filter(filterer).length +
          curr.aggregates.filter(filterer).length +
          curr.timeframes.filter(filterer).length
        const joins = reportTemplate.joins
          ? reportTemplate.joins.map(join => join.relatedTable)
          : []
        const tables = [reportTemplate.relatedTable].concat(joins)
        return this.topic ? tables.reduce(reducer, 0) : 0
      }
    },
    getReportTemplateLabelByDesign() {
      return designName =>
        this.topic
          ? this.topic.designs.find(design => design.name === designName).label
          : ''
    },
    getTitle() {
      return this.topic ? this.topic.label : ''
    }
  },
  created() {
    this.namespace = this.$route.params.namespace
    this.model = this.$route.params.model

    designApi
      .getTopic(this.namespace, this.model)
      .then(response => (this.topic = response.data))
      .catch(this.$error.handle)
    this.getDashboards()
      .then(() => (this.hasLoadedDashboards = true))
      .catch(this.$error.handle)
    this.getReports()
      .then(() => (this.hasLoadedReports = true))
      .catch(this.$error.handle)
  },
  methods: {
    ...mapActions('dashboards', ['getDashboards']),
    ...mapActions('reports', ['getReports']),
    goToDashboard(dashboard) {
      this.$router.push({ name: 'dashboard', params: dashboard })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    },
    goToReportTemplate(reportTemplate) {
      const params = {
        design: reportTemplate.name,
        model: this.model,
        namespace: this.namespace
      }
      this.$router.push({
        name: 'design',
        params
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
            <ConnectorLogo
              v-if="getExtractorName"
              :connector="getExtractorName"
            />
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
                    getReportTemplateLabelByDesign(report.design)
                  }}</small>
                </div>
                <div>
                  <button class="button is-small is-pulled-right ml-05r">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="content"><p>No reports</p></div>
          </template>
        </div>
      </div>

      <!-- Report Templates -->
      <div class="column">
        <div class="content">
          <h3 id="report-templates" class="title">Report Templates</h3>
          <p class="subtitle">Analysis starters</p>
        </div>
        <div class="box">
          <progress v-if="!topic" class="progress is-small is-info"></progress>
          <template v-else-if="topic.designs">
            <div class="list is-hoverable is-shadowless">
              <div
                v-for="reportTemplate in topic.designs"
                :key="reportTemplate.name"
                class="is-flex h-space-between list-item is-list-tight has-cursor-pointer"
                @click="goToReportTemplate(reportTemplate)"
              >
                <div>
                  <strong>{{ reportTemplate.label }}</strong>
                  <template v-if="reportTemplate.description">
                    <br />
                    <small>{{ reportTemplate.description }}</small>
                  </template>
                  <br />
                  <small class="is-italic has-text-grey"
                    >{{ getReportTemplateAttributesCount(reportTemplate) }} Data
                    Attributes</small
                  >
                </div>
                <div>
                  <button class="button is-small is-pulled-right ml-05r">
                    Analyze
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
