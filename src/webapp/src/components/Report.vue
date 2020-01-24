<script>
import { mapGetters } from 'vuex'
import Chart from '@/components/analyze/Chart'
import utils from '@/utils/utils'

export default {
  components: {
    Chart
  },
  props: {
    edit: {
      type: Boolean,
      required: true
    },
    index: {
      type: Number,
      required: true
    },
    report: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    position: 0,
    isEditable: false
  }),
  computed: {
    ...mapGetters('orchestration', ['lastUpdatedDate', 'startDate']),
    formattedLastUpdatedDate() {
      const extractor = `tap-${this.report.model}`
      return utils.formatDateStringYYYYMMDD(this.lastUpdatedDate(extractor))
    }
  },
  mounted() {
    this.position = this.index + 1
  },
  methods: {
    goToDesign(report) {
      const params = {
        design: report.design,
        model: report.model,
        namespace: report.namespace
      }
      this.$router.push({ name: 'analyzeDesign', params })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    },
    updatePosition() {
      const oldPosition = this.index
      const newPosition = this.position - 1
      const isUpdated = oldPosition !== newPosition

      if (isUpdated) {
        this.$emit('update-report-position', {
          oldPosition,
          newPosition,
          isUpdated
        })
      }
    }
  }
}
</script>

<template>
  <div class="column is-half" :class="edit ? 'wireframe' : ''">
    <div class="box">
      <div class="columns is-vcentered">
        <div class="column">
          <div class="is-grouped is-pulled-left">
            <h3 class="title is-5 is-inline-block mb-05r">{{ report.name }}</h3>
            <div class="has-text-grey is-size-6">
              Last updated: {{ formattedLastUpdatedDate }}
            </div>
          </div>
          <div v-if="edit" class="field is-pulled-right is-inline-block">
            <div>
              <label :for="`report-position-${index}`">Report Position: </label>
              <input
                :id="`report-position-${index}`"
                v-model.number="position"
                type="text"
                style="has-text-centered mb-05r"
                @focus="isEditable = true"
              />
            </div>
            <div
              v-show="isEditable"
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
        :class="edit ? 'is-transparent-50' : ''"
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
</style>
