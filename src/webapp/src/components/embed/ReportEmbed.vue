<script>
import Chart from '@/components/analyze/Chart'
import reportsApi from '@/api/reports'

export default {
  name: 'ReportEmbed',
  components: {
    Chart
  },
  props: {
    token: { type: String, default: null }
  },
  data() {
    return {
      isLoading: true,
      isValid: false,
      report: null
    }
  },
  created() {
    this.initialize()
  },
  methods: {
    initialize() {
      // swap to token/id consumed from from route
      reportsApi
        .loadFromEmbedToken(this.token)
        .then(response =>
          reportsApi.loadReportWithQueryResults(response.data['name'])
        )
        .then(response => {
          this.report = response.data
          this.isValid = true
          this.isLoading = false
        })
    }
  }
}
</script>

<template>
  <div>
    <progress v-if="!report" class="progress is-small is-info"></progress>

    <template v-else>
      <Chart
        v-if="isValid"
        :chart-type="report.chartType"
        :results="report.queryResults"
        :result-aggregates="report.queryResultAggregates"
      ></Chart>

      <div v-else class="content">
        <p>The requested embedded report is no longer public.</p>
      </div>
    </template>
  </div>
</template>

<style lang="scss"></style>
