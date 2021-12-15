<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'EditButton',
  props: {
    pipeline: { type: Object, required: true },
    isDisabled: { type: Boolean, required: false },
    isTooltipTop: { type: Boolean, required: false },
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
    goToEdit() {
      console.log('editing!')
    }
  }
}
</script>

<template>
  <button
    v-if="isAnalysisEnabled"
    class="button is-info editing-button tooltip"
    :class="[
      { 'is-loading': isDisabled, 'is-tooltip-top': isTooltipTop },
      customClass
    ]"
    :disabled="isDisabled || !getIsExplorable"
    data-tooltip="Edit pipeline details"
    @click="goToEdit"
  >
    <span class="icon is-small">
      <font-awesome-icon icon="edit"></font-awesome-icon>
    </span>
  </button>
</template>

<style lang="scss">
.editing-button {
  padding-right: 0.5em;
}
</style>
