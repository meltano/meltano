<template>
  <canvas ref="chart" height="200" v-show="results.length">A Chart</canvas>
</template>
<script>
import { mapState, mapGetters } from 'vuex';
import Chart from 'chart.js';
import utils from '../../api/utils';

export default {
  name: 'Bar',
  data() {
    return {
      chart: false,
    };
  },
  mounted() {
    this.createChart();
  },
  methods: {
    createChart() {
      const chart = this.$refs.chart.getContext('2d');
      this.chart = new Chart(chart, {
        type: 'horizontalBar',
        data: {
          labels: [],
          datasets: [{
            label: '',
            data: [],
            backgroundColor: 'rgba(103, 58, 183, 0.2)',
            borderColor: 'rgba(103, 58, 183, 0.2)',
            borderWidth: 2,
          }],
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero: true,
                callback: function callback(value, index, values) {
                  // total/amount of label = x
                  // show labels every 20 when greater than 20
                  const total = values.length;
                  const amount = 20;
                  const every = parseInt(total / amount, 10);
                  if (values.length > amount) {
                    if (index % every === 0) {
                      return value;
                    }
                    return '';
                  }
                  return value;
                },
              },
            }],
          },
        },
      });
      this.updateChart();
    },
    updateChart() {
      if (!this.results.length) return;
      this.chart.data.labels = [];
      this.chart.data.datasets = [];
      const resultsKeys = Object.keys(this.results[0]);
      const measures = Object.keys(this.resultMeasures);
      const diff = utils.difference(resultsKeys, measures);
      const dataSets = {};
      this.results.forEach((r) => {
        let label = [];
        resultsKeys.forEach((k, i) => {
          if (!diff.includes(k)) {
            const color = utils.getColor(i);
            if (!dataSets[k]) {
              dataSets[k] = {
                label: k,
                data: [],
                backgroundColor: color.backgroundColor,
                borderColor: color.borderColor,
                borderWidth: 1,
              };
            }
            dataSets[k].data.push(r[k]);
          } else {
            label.push(r[k]);
          }
        });
        label = utils.truncate(label.join('-'));
        this.chart.data.labels.push(label);
      });
      Object.keys(dataSets).forEach((k) => {
        this.chart.data.datasets.push(dataSets[k]);
      });
      this.chart.update();
    },
  },
  computed: {
    ...mapState('explores', [
      'results',
      'resultMeasures',
    ]),
    ...mapGetters('explores', [
      'getChartYAxis',
    ]),
  },
  watch: {
    results() {
      this.updateChart();
    },
  },
};
</script>
