<script>
import { mapGetters, mapState } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo
  },
  computed: {
    ...mapGetters('plugins', ['visibleExtractors']),
    ...mapGetters('orchestration', ['getHasPipelineWithExtractor']),
    ...mapState('orchestration', ['pipelines']),
    isLoadingExtractors() {
      return this.visibleExtractors && this.visibleExtractors.length === 0
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
    <div class="box is-borderless is-shadowless is-marginless">
      <progress
        v-if="isLoadingExtractors"
        class="progress is-small is-info"
      ></progress>

      <div v-else>
        <article
          v-for="(extractor, index) in visibleExtractors"
          :key="`${extractor.name}-${index}`"
          class="media has-cursor-pointer"
          :data-test-id="`${extractor.name}-extractor-card`"
          @click="updateExtractorSettings(extractor)"
        >
          <figure class="media-left">
            <p class="image level-item is-48x48 container">
              <ConnectorLogo :connector="extractor.name" />
            </p>
          </figure>
          <div class="media-content">
            <div class="content">
              <p>
                <strong>{{ extractor.label }}</strong>
                <br />
                <small>{{ extractor.description }}</small>
              </p>
            </div>
          </div>
          <figure
            v-if="getHasPipelineWithExtractor(extractor.name)"
            class="media-right"
          >
            <span
              class="icon has-text-success tooltip is-tooltip-right"
              data-tooltip="A pipeline for this data source already exists"
            >
              <font-awesome-icon icon="check"></font-awesome-icon>
            </span>
          </figure>
        </article>
      </div>
      <progress
        v-if="!visibleExtractors"
        class="progress is-small is-info"
      ></progress>
    </div>
  </div>
</template>

<style lang="scss"></style>
