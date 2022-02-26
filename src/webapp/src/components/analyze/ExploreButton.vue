<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'ExploreButton',
  props: {
    pipeline: { type: Object, required: true },
    isDisabled: { type: Boolean, required: false },
    isTooltipLeft: { type: Boolean, required: false },
    customClass: { type: String, required: false, default: '' }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin']),
    ...mapState('repos', ['models']),
    isAnalysisEnabled() {
      return !!this.$flask.isAnalysisEnabled
    },
    getExploreModel() {
      let targetModel
      for (const prop in this.models) {
        const model = this.models[prop]
        if (model.plugin_namespace === this.getNamespace) {
          targetModel = model
          break
        }
      }
      return targetModel
    },
    getIsExplorable() {
      return Boolean(this.getExploreModel)
    },
    getNamespace() {
      return this.getInstalledPlugin('extractors', this.pipeline.extractor)
        .namespace
    }
  },
  methods: {
    goToExplore() {
      this.$router.push({
        name: 'explore',
        params: { extractor: this.pipeline.extractor }
      })
    }
  }
}
</script>

<template>
  <div class="control">
    <button
      v-if="isAnalysisEnabled"
      class="button is-interactive-primary tooltip"
      :class="[
        { 'is-loading': isDisabled, 'is-tooltip-top': isTooltipLeft },
        customClass
      ]"
      :disabled="isDisabled || !getIsExplorable"
      data-tooltip="Explore dashboards, reports, templates, and more"
      @click="goToExplore"
    >
      <span>Explore</span>
      <span class="icon is-small">
        <font-awesome-icon icon="compass"></font-awesome-icon>
      </span>
    </button>
  </div>
</template>

<style lang="scss"></style>
