<script>
import { mapGetters, mapState } from 'vuex'

import ConnectorLogo from '@/components/generic/ConnectorLogo'
import ExploreButton from '@/components/analyze/ExploreButton'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo,
    ExploreButton
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsLoadingPluginsOfType',
      'getIsPluginInstalled',
      'visibleExtractors'
    ]),
    ...mapGetters('orchestration', [
      'getHasPipelineWithExtractor',
      'getPipelineWithExtractor'
    ]),
    ...mapState('orchestration', ['pipelines']),
    getColumns() {
      const length = this.visibleExtractors.length
      const halfLength = length / 2
      const columnOneLength = Math.ceil(halfLength)
      const columnOne = this.visibleExtractors.slice(0, columnOneLength)
      const columnTwo = this.visibleExtractors.slice(columnOneLength, length)
      return [columnOne, columnTwo]
    },
    getConnectionLabel() {
      return extractorName => {
        const connectLabel = this.getHasPipelineWithExtractor(extractorName)
          ? 'Edit Connection'
          : 'Connect'
        return this.getExtractorConfigurationNeedsFixing(extractorName)
          ? 'Fix Connection'
          : connectLabel
      }
    },
    getConnectionTooltip() {
      return extractorName => {
        return this.getHasPipelineWithExtractor(extractorName)
          ? 'Edit the connection details for this data source'
          : 'Install this data source and set up the connection'
      }
    },
    getConnectionStyle() {
      return extractorName => {
        const connectStyle = this.getHasPipelineWithExtractor(extractorName)
          ? ''
          : 'is-interactive-primary'
        return this.getExtractorConfigurationNeedsFixing(extractorName)
          ? 'is-danger'
          : connectStyle
      }
    },
    getExtractorConfigurationNeedsFixing() {
      return extractorName => {
        const pipeline = this.getPipelineWithExtractor(extractorName)
        return pipeline && !pipeline.isRunning && !pipeline.hasEverSucceeded
      }
    },
    getIsRelatedPipelineRunning() {
      return extractorName => {
        const pipeline = this.getPipelineWithExtractor(extractorName)
        return pipeline && pipeline.isRunning
      }
    },
    getPipeline() {
      return extractorName => this.getPipelineWithExtractor(extractorName)
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
                <span class="has-text-weight-bold">{{ extractor.label }}</span>
                <br />
                <small>{{ extractor.description }}</small>
                <template
                  v-if="getIsPluginInstalled('extractors', extractor.name)"
                >
                  <br />
                  <a
                    class="button is-static is-small is-borderless has-background-white"
                  >
                    <span class="icon" :class="`has-text-success`">
                      <font-awesome-icon
                        icon="check-circle"
                      ></font-awesome-icon>
                    </span>
                    <span class="has-text-grey is-italic">Installed</span>
                  </a>
                </template>
              </p>
              <div class="buttons">
                <ExploreButton
                  v-if="getHasPipelineWithExtractor(extractor.name)"
                  :pipeline="getPipeline(extractor.name)"
                />

                <router-link
                  v-if="getHasPipelineWithExtractor(extractor.name)"
                  class="button tooltip"
                  data-tooltip="View the pipeline for this data source"
                  tag="button"
                  to="pipelines"
                  >View Pipeline</router-link
                >

                <button
                  class="button tooltip"
                  :class="getConnectionStyle(extractor.name)"
                  :disabled="getIsRelatedPipelineRunning(extractor.name)"
                  :data-tooltip="getConnectionTooltip(extractor.name)"
                  @click="updateExtractorSettings(extractor)"
                >
                  <span>{{ getConnectionLabel(extractor.name) }}</span>
                </button>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
