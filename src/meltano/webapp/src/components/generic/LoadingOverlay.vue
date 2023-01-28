<script>
export default {
  name: 'LoadingOverlay',
  props: {
    isLoading: { type: Boolean, required: true, default: false },
  },
}
</script>

<!-- LoadingOverlay component instances expect a parent with a `position: relative;` -->
<template>
  <div v-if="isLoading" class="is-fill-space is-flex is-hcentered is-vcentered">
    <div class="is-fill-space loading-result-overlay"></div>
    <div class="loading-result-overlay-content">
      <button
        class="button is-loading is-borderless is-interactive-primary is-outlined"
      ></button>
    </div>
  </div>
</template>

<style lang="scss">
.loading-result-overlay {
  z-index: 1;
  background-color: $white;
  opacity: 0.5;
}

.loading-result-overlay-content {
  z-index: 2;
}
</style>
