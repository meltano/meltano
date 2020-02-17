<script>
import Chart from '@/components/analyze/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ReportEmbed',
  components: {
    Chart,
    ConnectorLogo
  },
  props: {
    report: { type: Object, default: null }
  },
  computed: {
    extractorName() {
      return this.report.namespace
        ? this.report.namespace.replace('model', 'tap')
        : ''
    }
  }
}
</script>

<template>
  <div>
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
  </div>
</template>

<style lang="scss"></style>
