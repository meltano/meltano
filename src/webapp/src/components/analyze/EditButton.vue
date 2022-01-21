<script>
export default {
  name: 'EditButton',
  props: {
    pipeline: { type: Object, required: true },
    isTooltipTop: { type: Boolean, required: false },
    customClass: { type: String, required: false, default: '' }
  },
  methods: {
    goToEdit(jobId) {
      this.$router.push({
        name: 'editPipelineSchedule',
        params: { jobId }
      })
    }
  }
}
</script>

<template>
  <button
    class="button editing-button is-info tooltip"
    :class="[{ 'is-tooltip-top': isTooltipTop }, customClass]"
    data-tooltip="Edit pipeline details"
    @click="goToEdit(pipeline.jobId)"
  >
    <span class="icon is-small">
      <font-awesome-icon icon="edit"></font-awesome-icon>
    </span>
  </button>
</template>

<style lang="scss">
.editing-button {
  padding: 0 0.5rem 0 0.65rem;
  background-color: #fff !important;
  color: #209cee !important;
  border: 1px solid #209cee !important;
  &:hover {
    background-color: #209cee !important;
    color: #fff !important;
    border: 1px solid #209cee !important;
  }
}
</style>
