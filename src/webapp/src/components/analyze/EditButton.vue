<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'EditButton',
  props: {
    pipeline: { type: Object, required: true },
    isTooltipTop: { type: Boolean, required: false },
    customClass: { type: String, required: false, default: '' }
  },
  //   computed: {
  //     ...mapGetters('plugins', ['getInstalledPlugin']),
  //     ...mapState('repos', ['models']),
  //     isAnalysisEnabled() {
  //       return !!this.$flask.isAnalysisEnabled
  //     },
  //     getExploreModel() {
  //       let targetModel
  //       for (const prop in this.models) {
  //         const model = this.models[prop]
  //         if (model.plugin_namespace === this.getNamespace) {
  //           targetModel = model
  //           break
  //         }
  //       }
  //       return targetModel
  //     },
  //     getIsExplorable() {
  //       return Boolean(this.getExploreModel)
  //     },
  //     getNamespace() {
  //       return this.getInstalledPlugin('extractors', this.pipeline.extractor)
  //         .namespace
  //     }
  //   },
  methods: {
    goToEdit() {
      console.log('editing!', this.pipeline)
      this.$router.push({
        name: 'editPipelineSchedule'
      })
    }
  }
}
</script>

<template>
  <button
    class="button is-info editing-button tooltip"
    :class="[{ 'is-tooltip-top': isTooltipTop }, customClass]"
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
