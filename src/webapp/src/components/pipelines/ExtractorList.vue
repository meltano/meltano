<script>
import { mapGetters, mapState } from 'vuex'
import ConnectorLogo from '@/components/generic/ConnectorLogo'

export default {
  name: 'ExtractorList',
  components: {
    ConnectorLogo
  },
  props: {
    focusedExtractor: { type: Object, default: null }
  },
  computed: {
    ...mapGetters('plugins', ['visibleExtractors']),
    ...mapGetters('orchestration', ['getHasPipelineWithExtractor']),
    ...mapState('orchestration', ['pipelines']),
    getIsActive() {
      return extractor => {
        return this.focusedExtractor
          ? this.focusedExtractor.name === extractor.name
          : false
      }
    },
    isLoadingExtractors() {
      return this.visibleExtractors && this.visibleExtractors.length === 0
    }
  },
  methods: {
    updateExtractorSettings(extractor) {
      if (this.getHasPipelineWithExtractor(extractor.name)) {
        return
      }
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
    <progress
      v-if="isLoadingExtractors"
      class="progress is-small is-info"
    ></progress>

    <div v-else>
      <article
        v-for="(extractor, index) in visibleExtractors"
        :key="`${extractor.name}-${index}`"
        class="media"
        :class="{
          'has-cursor-pointer is-hoverable': !getHasPipelineWithExtractor(
            extractor.name
          ),
          'is-active': getIsActive(extractor)
        }"
        :data-test-id="`${extractor.name}-extractor-card`"
        @click="updateExtractorSettings(extractor)"
      >
        <figure
          class="media-left"
          :class="{
            'is-transparent-50': getHasPipelineWithExtractor(extractor.name)
          }"
        >
          <p class="image level-item is-48x48 container">
            <ConnectorLogo
              :connector="extractor.name"
              :is-grayscale="getHasPipelineWithExtractor(extractor.name)"
            />
          </p>
        </figure>
        <div
          class="media-content"
          :class="{
            'is-transparent-50': getHasPipelineWithExtractor(extractor.name)
          }"
        >
          <div class="content">
            <p>
              <span class="has-text-weight-bold">{{ extractor.label }}</span>
              <br />
              <small>{{ extractor.description }}</small>
            </p>
          </div>
        </div>
        <figure
          v-if="getHasPipelineWithExtractor(extractor.name)"
          class="media-right is-flex is-flex-column is-vcentered"
        >
          <a
            href="#pipelines"
            class="button tooltip is-tooltip-left"
            data-tooltip="A pipeline for this data source already exists"
            @click.stop="() => {}"
          >
            <span>View Pipeline</span>
          </a>
        </figure>
      </article>
    </div>
    <progress
      v-if="!visibleExtractors"
      class="progress is-small is-info"
    ></progress>
  </div>
</template>

<style lang="scss"></style>
