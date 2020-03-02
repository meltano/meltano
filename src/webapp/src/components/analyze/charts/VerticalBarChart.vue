<script>
import chartMixin from './chartMixin'

export default {
  name: 'VerticalBarChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = 'bar'
    this.createChart()
  }
}
</script>

<template>
  <canvas v-show="results.length" ref="chart" height="200"></canvas>
</template>

<style lang="scss"></style>
