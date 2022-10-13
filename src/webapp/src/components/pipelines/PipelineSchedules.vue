<script>
import Pipeline from '@/components/pipelines/Pipeline'
import ScheduleTableHead from '@/components/pipelines/ScheduleTableHead'

export default {
  name: 'PipelineSchedules',
  components: {
    ScheduleTableHead,
    Pipeline,
  },
  props: {
    pipelines: { type: Array, required: true, default: () => [] },
  },
}
</script>

<template>
  <div class="box">
    <table class="table is-fullwidth is-hoverable is-size-7">
      <ScheduleTableHead has-actions has-start-date />
      <tbody>
        <template v-for="pipeline in pipelines">
          <Pipeline :key="pipeline.name" :pipeline="pipeline" />
        </template>
      </tbody>
    </table>
  </div>
</template>
<style lang="scss" scoped></style>
