<script>
import Chart from '@/components/analyze/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import Logo from '@/components/navigation/Logo'
import reportsApi from '@/api/reports'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'ReportEmbed',
  components: {
    Chart,
    ConnectorLogo,
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
  computed: {
    extractorName() {
      return this.report.namespace
        ? this.report.namespace.replace('model', 'tap')
        : ''
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
          <article class="media is-paddingless is-vcentered">
            <figure class="media-left">
              <p class="image level-item is-48x48 container">
                <ConnectorLogo :connector="extractorName" />
              </p>
            </figure>
            <h3 class="title is-5">
              {{ report.name }}
            </h3>
          </article>

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
