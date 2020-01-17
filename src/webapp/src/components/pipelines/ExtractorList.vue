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
    ...mapGetters('plugins', ['getIsPluginInstalled', 'visibleExtractors']),
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
          'is-hoverable': !getHasPipelineWithExtractor(extractor.name),
          'is-active': getIsActive(extractor)
        }"
        :data-test-id="`${extractor.name}-extractor-card`"
      >
        <figure
          class="media-left"
          :class="{
            ml1r: getIsActive(extractor)
          }"
        >
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
                    <font-awesome-icon icon="check-circle"></font-awesome-icon>
                  </span>
                  <span class="has-text-grey is-italic">Installed</span>
                </a>
              </template>
            </p>
          </div>
        </div>
        <figure class="media-right is-flex is-flex-column is-vcentered">
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
            v-else
            class="button is-interactive-primary tooltip is-tooltip-left"
            data-tooltip="A pipeline for this data source already exists"
            @click="updateExtractorSettings(extractor)"
          >
            <span>Connect</span>
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
