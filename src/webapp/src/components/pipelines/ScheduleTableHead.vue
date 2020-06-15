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
        <span>Data Source</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-right"
          data-tooltip="The pipeline's data source"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th>
        <span>Name</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-right"
          data-tooltip="The pipeline's name"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th>
        <span>Loader</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-left"
          data-tooltip="The pipeline's loader"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th>
        <span>Update Interval</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-left"
          data-tooltip="The pipeline's data refresh interval"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th v-if="hasStartDate">
        <span>Start Date</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-left"
          :class="{ 'is-tooltip-left': !hasActions }"
          data-tooltip="The pipeline's first date to extract data from"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th>
        <span>Transform</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-left"
          data-tooltip="The pipeline's transform type: 'Run','Only', 'Skip'"
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>

      <template v-if="hasActions">
        <th>
          <span>Last Run</span>
          <span
            class="icon has-text-grey-light tooltip is-tooltip-left"
            data-tooltip="The status of the last data refresh"
          >
            <font-awesome-icon icon="info-circle"></font-awesome-icon>
          </span>
        </th>
        <th class="has-text-right">
          <span>Actions</span>
        </th>
      </template>
    </tr>
  </thead>
</template>

<style lang="scss"></style>
