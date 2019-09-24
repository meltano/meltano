import Chart from 'chart.js'
import utils from '../../../utils/utils'

const chartMixin = {
  data() {
    return {
      chart: false,
      config: {
        type: 'horizontalBar',
        data: {
          labels: [],
          datasets: [
            {
              label: '',
              data: [],
              backgroundColor: 'rgba(103, 58, 183, 0.2)',
              borderColor: 'rgba(103, 58, 183, 0.2)',
              borderWidth: 2
            }
          ]
        },
        options: {
          scales: {
            xAxes: [
              {
                ticks: {
                  beginAtZero: true
                }
              }
            ],
            yAxes: [
              {
                ticks: {
                  beginAtZero: true,
                  callback: function callback(value, index, values) {
                    // total/amount of label = x
                    // show labels every 20 when greater than 20
                    const total = values.length
                    const amount = 20
                    const every = parseInt(total / amount, 10)
                    if (values.length > amount) {
                      if (index % every === 0) {
                        return value
                      }
                      return ''
                    }
                    return value
                  }
                }
              }
            ]
          }
        }
      }
    }
  },
  props: ['chartType', 'results', 'resultAggregates'],
  methods: {
    createChart() {
      const chart = this.$refs.chart.getContext('2d')
      this.chart = new Chart(chart, this.config)
      this.updateChart()
    },
    changeType() {
      const chart = this.$refs.chart.getContext('2d')
      this.config.type = this.chartType
      this.chart.destroy()
      this.chart = new Chart(chart, this.config)
      this.updateChart()
    },
    chartLabel(id) {
      const aggregate = this.resultAggregates.find(
        aggregate => aggregate.id === id
      )
      const hasDuplicate =
        this.resultAggregates.filter(item => item.label === aggregate.label)
          .length > 1

      return hasDuplicate
        ? `${aggregate.label} [Source: ${aggregate.source}]`
        : aggregate.label
    },
    updateChart() {
      if (!this.results.length) {
        return
      }
      this.chart.data.labels = []
      this.chart.data.datasets = []
      const fields = Object.keys(this.results[0])
      const aggregates = this.resultAggregates.map(item => item.id)
      const columns = utils.difference(fields, aggregates)
      const dataSets = {}
      this.results.forEach(r => {
        let label = []
        fields.forEach((k, i) => {
          // isn't this just aggregates?
          if (!columns.includes(k)) {
            const color = utils.getColor(i)
            if (!dataSets[k]) {
              dataSets[k] = {
                label: this.chartLabel(k),
                data: [],
                backgroundColor: color.backgroundColor,
                borderColor: color.borderColor,
                borderWidth: 1
              }
              if (this.chartType === 'LineChart') {
                dataSets[k].fill = false
              }
              if (this.chartType === 'ScatterChart') {
                dataSets[k].showLine = false
              }
            }
            dataSets[k].data.push(r[k])
          } else {
            label.push(r[k])
          }
        })
        label = utils.truncate(label.join('-'))
        this.chart.data.labels.push(label)
      })
      Object.keys(dataSets).forEach(k => {
        this.chart.data.datasets.push(dataSets[k])
      })
      this.chart.update()
    }
  },
  watch: {
    results() {
      this.updateChart()
    },
    chartType() {
      this.changeType()
    }
  }
}

export default chartMixin
