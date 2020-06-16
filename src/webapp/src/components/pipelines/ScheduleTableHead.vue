<script>
export default {
  name: 'ScheduleTableHead',
  props: {
    hasActions: { type: Boolean, default: false },
    hasStartDate: { type: Boolean, default: false }
  }
}
</script>

<template>
  <thead>
    <tr>
      <th>
        Data Source
      </th>
      <th>
        Name
      </th>
      <th>
        Loader
      </th>
      <th>
        Update Interval
      </th>
      <th v-if="hasStartDate">
        Start Date
      </th>
      <th>
        Transform
      </th>

      <template v-if="hasActions">
        <th>
          Last Run
        </th>
        <th class="has-text-right">
          Actions
        </th>
      </template>
    </tr>
  </thead>
</template>

<style lang="scss"></style>
