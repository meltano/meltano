<script>
export default {
  name: 'SpeedRunIcon',
  props: {
    tooltip: {
      type: String,
      default: 'No authentication or setup required!'
    }
  }
}
</script>

<template>
  <div class="sri-wrapper">
    <span
      class="icon has-text-grey-light tooltip is-tooltip-right"
      :data-tooltip="tooltip"
    >
      <svg
        version="1.1"
        id="Layer_1"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        x="0px"
        y="0px"
        viewBox="0 0 512 512"
        style="enable-background:new 0 0 512 512;"
        xml:space="preserve"
        width="30"
        height="30"
      >
        <path
          style="fill:#ECBA16;"
          d="M397.241,176.552H276.303L388.414,0H247.172L114.759,264.828h104.166L114.759,512L397.241,176.552z"
        />
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
        <g></g>
      </svg>
    </span>
  </div>
</template>

<style lang="scss" scoped>
.sri-wrapper {
  position: absolute;
  right: 20px;
  top: 25px;
}
</style>
