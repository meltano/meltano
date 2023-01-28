<script>
import { mapGetters } from 'vuex'

export default {
  name: 'ConnectorLogo',
  props: {
    connector: { type: String, required: true, default: '' },
    type: { type: String, default: 'extractors' },
    isGrayscale: { type: Boolean, default: false },
  },
  computed: {
    ...mapGetters('plugins', ['getPluginLogoUrl']),
    connectorLogoUrl() {
      return this.getPluginLogoUrl(this.type, this.connector)
    },
  },
}
</script>

<template>
  <img :class="{ grayscale: isGrayscale }" :src="connectorLogoUrl" alt="" />
</template>

<style lang="scss"></style>
