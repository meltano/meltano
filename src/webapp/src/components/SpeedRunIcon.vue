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
    <p
      class="has-text-grey-light tooltip is-tooltip-top is-flex"
      :data-tooltip="tooltip"
      style="justify-content: center;"
    >
      <span class="sri-label">Fast Path</span>
      <font-awesome-icon icon="bolt" color="#ffd700"></font-awesome-icon>
    </p>
  </div>
</template>

<style lang="scss" scoped>
.sri-label {
  margin-right: 5px;
}

.sri-wrapper {
  position: absolute;
  right: 20px;
  top: 25px;
  display: flex;
  align-items: center;
}

.svg-inline--fa {
  height: auto;
}
</style>
