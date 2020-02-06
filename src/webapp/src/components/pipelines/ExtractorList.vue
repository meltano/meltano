<script>
import { mapGetters, mapState } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo
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
    getConnectionLabel() {
      return extractorName => {
        const connectLabel = this.getHasPipelineWithExtractor(extractorName)
          ? 'View Connection'
          : 'Connect'
        return this.getExtractorConfigurationNeedsFixing(extractorName)
          ? 'Fix Connection'
          : connectLabel
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
      return extractorName =>
        this.getHasPipelineWithExtractor(extractorName) &&
        !this.getPipelineWithExtractor(extractorName).hasEverSucceeded
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
  <div>
    <article
      v-for="(extractor, index) in visibleExtractors"
      :key="`${extractor.name}-${index}`"
      class="media is-hoverable"
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
            <template v-if="getIsPluginInstalled('extractors', extractor.name)">
              <br />
              <a
                class="button is-static is-small is-borderless has-background-white"
              >
                <span class="icon" :class="`has-text-success`">
                  <font-awesome-icon icon="check-circle"></font-awesome-icon>
                </span>
                <span class="has-text-grey is-italic">Installed</span>
              </a>
            </template>
          </p>
        </div>
      </div>
      <figure class="media-right is-flex is-flex-column is-vcentered">
        <div class="buttons">
          <a
            v-if="getHasPipelineWithExtractor(extractor.name)"
            href="#pipelines"
            class="button tooltip is-tooltip-left"
            data-tooltip="A pipeline for this data source already exists"
            @click.stop="() => {}"
          >
            <span>View Pipeline</span>
          </a>
          <a
            class="button tooltip is-tooltip-left"
            :class="getConnectionStyle(extractor.name)"
            data-tooltip="Install and connect to this data source"
            @click="updateExtractorSettings(extractor)"
          >
            <span>{{ getConnectionLabel(extractor.name) }}</span>
          </a>
        </div>
      </figure>
    </article>
  </div>
</template>

<style lang="scss"></style>
