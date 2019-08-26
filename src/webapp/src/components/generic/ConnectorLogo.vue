<script>
import utils from '@/utils/utils'

export default {
  name: 'ConnectorLogo',
  props: {
    connector: { type: String, required: true, default: '' },
    isGrayscale: { type: Boolean, default: false }
  },
  computed: {
    connectorLogoUrl() {
      return utils.getConnectorLogoUrl(this.connector)
    }
  }
}
</script>

<template>
  <img
    :class="{ grayscale: isGrayscale }"
    :src="connectorLogoUrl"
    :alt="`${connector} logo`"
  />
</template>

<style lang="scss"></style>
