<script>
import { mapGetters, mapState } from 'vuex'

import Chart from '@/components/analyze/Chart'
import ResultLoadingOverlay from '@/components/analyze/ResultLoadingOverlay'

export default {
  name: 'ResultTable',
  components: {
    Chart,
    ResultLoadingOverlay
  },
  props: {
    isLoading: { type: Boolean, required: true, default: false }
  },
  computed: {
    ...mapState('designs', ['chartType', 'results', 'resultAggregates']),
    ...mapGetters('designs', [
      'getAllAttributes',
      'hasChartableResults',
      'hasResults'
    ]),
    getHasMinimalSelectionRequirements() {
      const selected = attribute => attribute.selected
      const hasAggregate = this.getAllAttributes(['aggregates']).find(selected)
      return hasAggregate
    }
  }
}
</script>

<template>
  <div class="has-position-relative v-min-2r">
    <ResultLoadingOverlay :is-loading="isLoading"></ResultLoadingOverlay>

    <div v-if="hasChartableResults">
      <Chart
        :chart-type="chartType"
        :results="results"
        :result-aggregates="resultAggregates"
      ></Chart>
    </div>

    <div v-else-if="!getHasMinimalSelectionRequirements">
      <article class="message is-info">
        <div class="message-body">
          <div class="content">
            <p>To display a <em>Chart</em>:</p>
            <ol>
              <li>
                Select at least one
                <strong>Aggregate</strong> from the <em>Attributes</em> panel
              </li>
              <li>
                Manually click the <em>Run</em> button (if
                <em>Autorun Queries</em> is toggled off)
              </li>
            </ol>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style lang="scss"></style>
