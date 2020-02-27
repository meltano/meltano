<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'ExploreButton',
  props: {
    pipeline: { type: Object, required: true },
    isDisabled: { type: Boolean, required: false }
  },
  computed: {
    ...mapGetters('plugins', ['getInstalledPlugin']),
    ...mapState('repos', ['models'])
  },
  methods: {
    goToExplore() {
      // Split based on '@' profiles convention
      const extractor = this.pipeline.extractor.split('@')[0]
      const namespace = this.getInstalledPlugin('extractors', extractor)
        .namespace
      for (const prop in this.models) {
        const model = this.models[prop]
        if (model.plugin_namespace === namespace) {
          const { name, namespace } = model
          this.$router.push({
            name: 'explore',
            params: { model: name, namespace }
          })
        }
      }
    }
  }
}
</script>

<template>
  <button
    class="button is-interactive-primary tooltip is-tooltip-left"
    :class="{ 'is-loading': isDisabled }"
    :disabled="isDisabled"
    data-tooltip="Explore dashboards, reports, report templates, and more"
    @click="goToExplore"
  >
    <span>Explore</span>
    <span class="icon is-small">
      <font-awesome-icon icon="chart-line"></font-awesome-icon>
    </span>
  </button>
</template>

<style lang="scss"></style>
