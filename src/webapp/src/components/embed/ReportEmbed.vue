<script>
import Chart from '@/components/analyze/Chart'
import reportsApi from '@/api/reports'

export default {
  name: 'ReportEmbed',
  components: {
    Chart
  },
  props: {
    token: { type: String, required: false }
  },
  data() {
    return {
      isLoading: true,
      report: null
    }
  },
  created() {
    this.initialize()
  },
  methods: {
    initialize() {
      // swap to token/id consumed from from route
      const name = 'Test Report'
      reportsApi.loadReportWithQueryResults(name).then(response => {
        this.report = response.data
        this.isLoading = false
      })
    }
  }
}
</script>

<template>
  <div>
    <progress v-if="!report" class="progress is-small is-info"></progress>

    <Chart
      v-else
      :chart-type="report.chartType"
      :results="report.queryResults"
      :result-aggregates="report.queryResultAggregates"
    ></Chart>
  </div>
</template>

<style lang="scss"></style>
