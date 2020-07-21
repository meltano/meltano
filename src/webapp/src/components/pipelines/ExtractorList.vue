<script>
import { mapGetters, mapState } from 'vuex'
import pluralize from 'pluralize'

import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo
  },
  props: {
    items: {
      type: Array,
      required: true
    }
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled']),
    ...mapGetters('orchestration', [
      'getHasPipelineWithExtractor',
      'getPipelinesWithExtractor'
    ]),
    ...mapState('orchestration', ['pipelines']),
    getColumns() {
      const length = this.items.length
      const halfLength = length / 2
      const columnOneLength = Math.ceil(halfLength)
      const columnOne = this.items.slice(0, columnOneLength)
      const columnTwo = this.items.slice(columnOneLength, length)
      return [columnOne, columnTwo]
    },
    getConnectionLabel() {
      return extractorName => {
        return this.getIsPluginInstalled('extractors', extractorName)
          ? 'Configure'
          : 'Add to project'
      }
    },
    getConnectionStyle() {
      return extractorName => {
        return this.getIsPluginInstalled('extractors', extractorName)
          ? ''
          : 'is-interactive-primary'
      }
    },

    getPipelinesTooltip() {
      return extractorName => {
        const extractorPipelines = this.getPipelinesWithExtractor(extractorName)
        if (extractorPipelines.length) {
          const pipelineNames = extractorPipelines.map(el => el.name)
          return pipelineNames.join(', ')
        } else {
          return 'Create a pipeline'
        }
      }
    },
    getExtractorButtonLabel() {
      return extractorName => {
        const pipelineAmount = this.getPipelinesWithExtractor(extractorName)
          .length
        return pluralize('pipeline', pipelineAmount, true)
      }
    },
    getExtractorButtonRoute() {
      return extractorName => {
        const pipelineAmount = this.getPipelinesWithExtractor(extractorName)
          .length
        if (pipelineAmount) {
          return {
            name: 'pipelines'
          }
        }
        return {
          name: 'createPipelineSchedule',
          query: {
            extractor: extractorName
          }
        }
      }
    }
  },
  methods: {
    updateExtractorSettings(extractor) {
      this.$emit('select', extractor)
      this.$router.push({
        name: 'extractorSettings',
        params: { extractor: extractor.name }
      })
    }
  }
}
</script>

<template>
  <div class="columns">
    <div v-for="(column, idx) in getColumns" :key="idx" class="column">
      <div
        v-for="(extractor, index) in column"
        :key="`${extractor.name}-${index}`"
      >
        <article
          class="media"
          :data-test-id="`${extractor.name}-extractor-card`"
        >
          <figure class="media-left">
            <p class="image level-item is-48x48 container">
              <ConnectorLogo :connector="extractor.name" />
            </p>
          </figure>
          <div class="media-content">
            <div class="content">
              <p>
                <span class="has-text-weight-bold">{{
                  extractor.label || extractor.name
                }}</span>
                <br />
                <small>{{ extractor.description }}</small>
              </p>
              <div class="buttons">
                <button
                  class="button"
                  :class="getConnectionStyle(extractor.name)"
                  @click="updateExtractorSettings(extractor)"
                >
                  <span>{{ getConnectionLabel(extractor.name) }}</span>
                </button>
                <router-link
                  v-if="getIsPluginInstalled('extractors', extractor.name)"
                  class="button tooltip is-borderless"
                  :data-tooltip="getPipelinesTooltip(extractor.name)"
                  tag="button"
                  :to="getExtractorButtonRoute(extractor.name)"
                >
                  <span
                    class="icon is-small"
                    :class="
                      getHasPipelineWithExtractor(extractor.name)
                        ? 'has-text-success'
                        : 'has-text-danger'
                    "
                  >
                    <font-awesome-icon
                      :icon="
                        getHasPipelineWithExtractor(extractor.name)
                          ? 'check-circle'
                          : 'exclamation-triangle'
                      "
                    ></font-awesome-icon>
                  </span>
                  <span>
                    {{ getExtractorButtonLabel(extractor.name) }}
                  </span>
                </router-link>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
