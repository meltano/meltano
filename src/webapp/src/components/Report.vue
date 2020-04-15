<script>
import { mapGetters } from 'vuex'

import Chart from '@/components/analyze/charts/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import EmbedShareButton from '@/components/generic/EmbedShareButton'
import reportDateRangeMixin from '@/components/analyze/reportDateRangeMixin'

export default {
  components: {
    Chart,
    ConnectorLogo,
    EmbedShareButton
  },
  mixins: [reportDateRangeMixin],
  props: {
    isEditing: {
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
    position: 0
  }),
  computed: {
    ...mapGetters('orchestration', ['lastUpdatedDate']),

    dataLastUpdatedDate() {
      const date = this.lastUpdatedDate(this.extractorName)

      return date ? date : 'Unknown'
    },
    extractorName() {
      return this.report.namespace
        ? this.report.namespace.replace('model', 'tap')
        : ''
    },
    positionChanged() {
      return this.position != this.index + 1
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
      this.$router.push({ name: 'design', params })
    },
    goToReport(report) {
      this.$router.push({ name: 'report', params: report })
    },
    updatePosition() {
      const oldIndex = this.index
      const newIndex = this.position - 1

      this.$emit('update-report-index', {
        oldIndex,
        newIndex
      })
    }
  }
}
</script>

<template>
  <div class="column is-half" :class="isEditing ? 'wireframe' : ''">
    <div class="box">
      <article class="media is-paddingless">
        <figure class="media-left">
          <p class="image level-item is-48x48 container">
            <ConnectorLogo :connector="extractorName" />
          </p>
        </figure>
        <div class="media-content">
          <div class="content">
            <p>
              <strong>{{ report.name }}</strong>
              <small v-if="hasDateRange" class="has-text-grey is-size-7">
                <br />
                Date range: {{ dateRangeLabel }}
              </small>
              <small class="has-text-grey is-size-7">
                <br />
                Last updated: {{ dataLastUpdatedDate }}
              </small>
            </p>
          </div>
        </div>
        <div class="media-right">
          <div v-if="isEditing" class="field is-pulled-right is-inline-block">
            <div>
              <label :for="`report-position-${index}`">Report Position: </label>
              <input
                :id="`report-position-${index}`"
                v-model.number="position"
                type="text"
                style="has-text-centered mb-05r"
                @focus="positionChanged = true"
              />
            </div>
            <div
              v-if="positionChanged"
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
              <EmbedShareButton
                :resource="report"
                resource-type="report"
                button-classes="is-small"
              />
            </div>
          </div>
        </div>
      </article>

      <br />

      <Chart
        :class="isEditing ? 'is-transparent-50' : ''"
        :chart-type="report.chartType"
        :results="report.queryResults"
        :result-aggregates="report.queryResultAggregates"
      />
    </div>
  </div>
</template>

<style>
.wireframe {
  border: 3px dotted #ddd;
}
</style>
