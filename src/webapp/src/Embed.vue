<script>
import Chart from '@/components/analyze/Chart'
import reportsApi from '@/api/reports'

export default {
  name: 'Embed',
  components: {
    Chart
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
  <div id="app">
    <progress v-if="!report" class="progress is-small is-info"></progress>

    <Chart
      v-else
      :chart-type="report.chart_type"
      :results="report.query_results"
      :result-aggregates="report.query_result_aggregates"
    ></Chart>
  </div>
</template>

<style lang="scss">
@import 'scss/_index.scss';
</style>
