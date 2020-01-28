<script>
import { mapGetters } from 'vuex'
import Vue from 'vue'

import Chart from '@/components/analyze/Chart'
import Dropdown from '@/components/generic/Dropdown'
import reportsApi from '@/api/reports'
import utils from '@/utils/utils'

export default {
  components: {
    Chart,
    Dropdown
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
    isAwaitingEmbed: false,
    isEditable: false
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
    copyToClipboard(refName) {
      const el = this.$refs[refName]
      const isSuccess = utils.copyToClipboard(el)
      isSuccess
        ? Vue.toasted.global.success('Copied to clipboard')
        : Vue.toasted.global.error('Failed copy, try manual selection')
    },
    getReportEmbed(report) {
      this.isAwaitingEmbed = true
      reportsApi
        .generateEmbedURL(report)
        .then(response => {
          this.$refs[`embed-${report.id}`].value = response.data.snippet
          if (response.data.isNew) {
            Vue.toasted.global.success(`${report.name} embed code created`)
          }
        })
        .catch(error => {
          Vue.toasted.global.error(
            `${report.name} embed error. [Error code: ${error.response.data.code}]`
          )
        })
        .finally(() => (this.isAwaitingEmbed = false))
    },
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
              Last updated: {{ dataLastUpdatedDate }}
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
              <Dropdown
                :tooltip="{
                  classes: 'is-tooltip-left',
                  message: 'Create an embeddable iframe'
                }"
                label="Embed"
                button-classes="button is-small"
                :menu-classes="'dropdown-menu-300'"
                :disabled="isAwaitingEmbed"
                is-right-aligned
                @dropdown:open="getReportEmbed(report)"
              >
                <div class="dropdown-content is-size-7">
                  <div class="dropdown-item">
                    <div class="field has-addons">
                      <p class="control is-expanded">
                        <input
                          :ref="`embed-${report.id}`"
                          class="input is-small is-family-code has-background-white-ter	has-text-grey-dark	"
                          type="text"
                          placeholder="Generating snippet..."
                          readonly
                        />
                      </p>
                      <p class="control">
                        <button
                          class="button is-small"
                          :disabled="isAwaitingEmbed"
                          @click="copyToClipboard(`embed-${report.id}`)"
                        >
                          Copy Snippet
                        </button>
                      </p>
                    </div>
                  </div>
                  <div class="dropdown-item">
                    <p class="is-italic is-size-7">
                      This report is now
                      <strong>publicly embeddable</strong>. It is only public
                      when embedded on another website.
                    </p>
                  </div>
                </div>
              </Dropdown>
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
