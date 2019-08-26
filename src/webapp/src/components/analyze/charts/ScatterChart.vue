<script>
import chartMixin from './chartMixin'

export default {
  name: 'ScatterChart',
  mixins: [chartMixin],
  mounted() {
    this.config.type = 'line'
    this.createChart()
  }
}
</script>

<template>
  <canvas v-show="results.length" ref="chart" height="200"></canvas>
</template>

<style lang="scss"></style>
