<script>
import Chart from '@/components/analyze/Chart'

export default {
  components: {
    Chart
  },
  props: {
    index: {
      type: Number,
      required: true
    },
    edit: {
      type: Boolean,
      required: true
    },
    report: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    position: 0,
    showMoveAction: false
  }),
  mounted() {
    this.position = this.index + 1
  },
  methods: {
    updatePosition() {
      let isUpdated = this.index !== this.position - 1

      this.$emit('update-report-position', {
        oldPosition: this.index,
        newPosition: this.position - 1,
        isUpdated
      })
    }
  }
}
</script>

<template>
  <div class="column is-half" :class="edit ? 'wireframe' : ''">
    <div class="box">
      <div class="columns is-vcentered">
        <div class="column">
          <h3 class="title is-5 is-inline-block">{{ report.name }}</h3>
          <div v-if="edit" class="field is-pulled-right is-inline-block">
            <div>
              <label :for="`report-position-${index}`">Report Position: </label>
              <input
                :id="`report-position-${index}`"
                v-model.number="position"
                type="text"
                style="has-text-centered mb-05r"
                @focus="showMoveAction = true"
              />
            </div>
            <div
              v-show="showMoveAction"
              class="field is-pulled-right is-inline-block"
            >
              <button
                class="button is-small is-primary"
                @click="updatePosition"
              >
                Update Position
              </button>
            </div>
          </div>

          <div v-else class="field is-pulled-right is-inline-block">
            <div class="buttons">
              <a class="button is-small" @click="goToReport(report)">Edit</a>
              <a class="button is-small" @click="goToDesign(report)">Explore</a>
            </div>
          </div>
        </div>
      </div>

      <chart
        :class="edit ? 'fade' : ''"
        :chart-type="report.chartType"
        :results="report.queryResults"
        :result-aggregates="report.queryResultAggregates"
      ></chart>
    </div>
  </div>
</template>

<style>
.wireframe {
  color: red;
  border: 3px dotted #ddd;
}

.fade {
  opacity: 0.5;
}

.mb-05r {
  margin-bottom: 0.5rem;
}
</style>
