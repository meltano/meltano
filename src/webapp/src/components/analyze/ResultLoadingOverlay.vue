<script>
export default {
  name: 'ResultLoadingOverlay',
  props: {
    isLoading: { type: Boolean, required: true, default: false }
  }
}
</script>

<template>
  <div v-if="isLoading" class="is-loading-result-overlay">
    <button
      class="button is-static has-background-white is-borderless is-loading"
    ></button>
  </div>
</template>

<style lang="scss">
.is-loading-result-overlay {
  position: absolute;
  z-index: 1;
  background-color: white;
  opacity: 0.4;
  width: 100%;
  height: 100%;
}
</style>
