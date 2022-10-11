<script>
export default {
  name: 'ScheduleTableHead',
  props: {
    hasActions: { type: Boolean, default: false },
    hasStartDate: { type: Boolean, default: false },
  },
}
</script>

<template>
  <thead>
    <tr>
      <th>Name</th>
      <th>Extractor</th>
      <th>Loader</th>
      <th>Transform</th>
      <th>Interval</th>
      <th v-if="hasStartDate">Start Date</th>
      <template v-if="hasActions">
        <th>Last Run</th>
        <th>Actions</th>
      </template>
    </tr>
  </thead>
</template>

<style lang="scss"></style>
