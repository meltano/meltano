<script>
import chartMixin from './chartMixin'

export default {
  name: 'BarChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = 'horizontalBar'
    this.createChart()
  }
}
</script>

<template>
  <canvas v-show="results.length" ref="chart" height="200"></canvas>
</template>

<style lang="scss"></style>
