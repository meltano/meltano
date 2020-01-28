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
      errorMessage: null,
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
      reportsApi
        .loadFromEmbedToken(this.token)
        .then(response => {
          this.report = response.data
          this.isValid = true
        })
        .catch(error => {
          this.errorMessage = error.response.data.code
          this.isValid = false
        })
        .finally(() => (this.isLoading = false))
    }
  }
}
</script>

<template>
  <div>
    <progress v-if="isLoading" class="progress is-small is-info"></progress>

    <template v-else>
      <Chart
        v-if="isValid"
        :chart-type="report.chartType"
        :results="report.queryResults"
        :result-aggregates="report.queryResultAggregates"
      ></Chart>

      <div v-else class="content">
        <p>{{ errorMessage }}</p>
      </div>
    </template>
  </div>
</template>

<style lang="scss"></style>
