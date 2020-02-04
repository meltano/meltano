<script>
import Chart from '@/components/analyze/Chart'
import Logo from '@/components/navigation/Logo'
import reportsApi from '@/api/reports'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'ReportEmbed',
  components: {
    Chart,
    Logo,
    RouterViewLayout
  },
  props: {
    token: { type: String, default: null }
  },
  data() {
    return {
      error: null,
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
          this.error = error.response.data.code
          this.isValid = false
        })
        .finally(() => (this.isLoading = false))
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="box is-marginless">
      <progress v-if="isLoading" class="progress is-small is-info"></progress>

      <template v-else>
        <template v-if="isValid">
          <div class="is-grouped is-pulled-left">
            <h3 class="title is-5 is-inline-block mb-05r">
              {{ report.name }}
            </h3>
          </div>
          <Chart
            :chart-type="report.chartType"
            :results="report.queryResults"
            :result-aggregates="report.queryResultAggregates"
          />
        </template>
        <div v-else class="content has-text-centered">
          <p class="is-italic">{{ error }}</p>
        </div>
      </template>
    </div>

    <div class="is-pulled-right mt-05r scale-08">
      <a href="https://meltano.com" target="_blank" class="is-size-7">
        <span class="is-inline-block has-text-grey">Made with</span>
        <Logo class="ml-05r"
      /></a>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
.scale-08 {
  transform: scale(0.8);
}
</style>
