<script>
import { mapGetters } from 'vuex'

import Chart from '@/components/analyze/charts/Chart'
import ConnectorLogo from '@/components/generic/ConnectorLogo'
import Dropdown from '@/components/generic/Dropdown'
import EmbedShareButton from '@/components/generic/EmbedShareButton'
import reportDateRangeMixin from '@/components/analyze/reportDateRangeMixin'

export default {
  components: {
    Chart,
    ConnectorLogo,
    Dropdown,
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
    },
    removeFromDashboard() {
      this.$emit('remove-from-dashboard', this.index)
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
            <div class="field is-grouped">
              <Dropdown
                label="Move"
                class="control"
                button-classes="is-small"
                menu-classes="dropdown-menu-300"
                is-right-aligned
              >
                <div class="dropdown-content">
                  <div class="dropdown-item">
                    <div class="field">
                      <label class="label">Move to position</label>
                      <div class="control">
                        <input
                          v-model.number="position"
                          class="input"
                          type="text"
                        />
                      </div>
                    </div>
                    <div class="buttons is-right">
                      <button class="button is-text" data-dropdown-auto-close>
                        Cancel
                      </button>
                      <button
                        class="button"
                        :disabled="!positionChanged"
                        data-dropdown-auto-close
                        @click="updatePosition"
                      >
                        Update
                      </button>
                    </div>
                  </div>
                </div>
              </Dropdown>

              <Dropdown
                button-classes="is-danger is-outlined is-small"
                class="control"
                :tooltip="{
                  classes: 'is-tooltip-left',
                  message: 'Remove report from dashboard'
                }"
                menu-classes="dropdown-menu-300"
                icon-open="trash-alt"
                icon-close="caret-up"
                is-right-aligned
              >
                <div class="dropdown-content is-unselectable">
                  <div class="dropdown-item">
                    <div class="content">
                      <p>
                        Are you sure you want to remove this report from the
                        dashboard?
                      </p>
                    </div>
                    <div class="buttons is-right">
                      <button class="button is-text" data-dropdown-auto-close>
                        Cancel
                      </button>
                      <button
                        class="button is-danger"
                        data-dropdown-auto-close
                        @click="removeFromDashboard"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              </Dropdown>
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
