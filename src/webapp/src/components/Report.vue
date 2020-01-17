<script>
import Chart from '@/components/analyze/Chart'

export default {
  components: {
    Chart
  },
  props: {
    report: {
      type: Object,
      required: true
    }
  }
}
</script>

<template>
  <div class="column is-half">
    <div class="box">
      <div class="columns is-vcentered">
        <div class="column">
          <h3 class="title is-5 is-inline-block">{{ report.name }}</h3>
          <div class="field is-pulled-right is-inline-block">
            <input type="number" />
            <div class="buttons">
              <button class="button is-small">Rearrange</button>
              <a class="button is-small" @click="goToReport(report)">Edit</a>
              <a class="button is-small" @click="goToDesign(report)">Explore</a>
            </div>
          </div>
        </div>
      </div>

      <chart
        :chart-type="report.chartType"
        :results="report.queryResults"
        :result-aggregates="report.queryResultAggregates"
      ></chart>
    </div>
  </div>
</template>

<style></style>
