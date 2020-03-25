<script>
import Chart from '@/components/analyze/charts/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import reportDateRangeMixin from '@/components/analyze/reportDateRangeMixin'

export default {
  name: 'ReportEmbed',
  components: {
    Chart,
    ConnectorLogo
  },
  mixins: [reportDateRangeMixin],
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
      <div class="media-content">
        <h3 class="title is-5">{{ report.name }}</h3>
      </div>
      <div v-if="hasDateRange" class="media-right">
        <div class="field is-pulled-right is-inline-block">
          <small class="has-text-grey is-size-7">{{ dateRangeLabel }}</small>
        </div>
      </div>
    </article>

    <Chart
      :chart-type="report.chartType"
      :results="report.queryResults"
      :result-aggregates="report.queryResultAggregates"
    />
  </div>
</template>

<style lang="scss"></style>
