<script>
import { mapGetters, mapState } from 'vuex'

import Chart from '@/components/analyze/Chart'
import LoadingOverlay from '@/components/generic/LoadingOverlay'
import { selected } from '@/utils/predicates'

export default {
  name: 'ResultTable',
  components: {
    Chart,
    LoadingOverlay
  },
  props: {
    isLoading: { type: Boolean, default: false }
  },
  computed: {
    ...mapState('designs', ['chartType', 'results', 'resultAggregates']),
    ...mapGetters('designs', [
      'getAttributes',
      'hasChartableResults',
      'hasResults'
    ]),
    getHasMinimalSelectionRequirements() {
      return this.getAttributes(['aggregates']).find(selected)
    }
  }
}
</script>

<template>
  <div class="has-position-relative v-min-2r">
    <LoadingOverlay :is-loading="isLoading"></LoadingOverlay>

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
