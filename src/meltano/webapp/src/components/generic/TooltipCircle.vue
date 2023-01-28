<script>
export default {
  name: 'TooltipCircle',
  props: {
    text: {
      type: String,
      required: true,
    },
  },
}
</script>

<template>
  <div class="is-inline-block">
    <a
      class="button tooltip is-tooltip-multiline"
      :class="$style['tooltip-circle']"
      :data-tooltip="text"
    >
      <span>?</span>
    </a>
  </div>
</template>

<style lang="scss" module>
.tooltip-circle {
  width: 15px;
  height: 15px;
  padding: 0;
  font-size: 0.7rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $grey-light;
  color: $white;
}
</style>
