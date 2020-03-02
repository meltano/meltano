<script>
import { mapGetters } from 'vuex'

import Chart from '@/components/analyze/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import EmbedShareButton from '@/components/generic/EmbedShareButton'

export default {
  components: {
    Chart,
    ConnectorLogo,
    EmbedShareButton
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
    isEditable: false,
    position: 0
  }),
  computed: {
    ...mapGetters('orchestration', ['lastUpdatedDate']),

    dataLastUpdatedDate() {
      const date = this.lastUpdatedDate(this.extractorName)

      return date ? date : 'Not available'
    },

    extractorName() {
      return this.report.namespace
        ? this.report.namespace.replace('model', 'tap')
        : ''
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
              <br />
              <small class="has-text-grey"
                >Last updated: {{ dataLastUpdatedDate }}</small
              >
            </p>
          </div>
        </div>
        <div class="media-right">
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
        :class="edit ? 'is-transparent-50' : ''"
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
