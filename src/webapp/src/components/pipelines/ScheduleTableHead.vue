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
        <span>Name</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-right"
          data-tooltip="The unique identifier for an ELT pipeline schedule and its settings."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class="has-text-centered">
        <span>Extractor</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-bottom"
          data-tooltip="The connector for data extraction within a scheduled ELT pipeline."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class="has-text-centered">
        <span>Loader</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-bottom"
          data-tooltip="The connector for data loading within a scheduled ELT pipeline."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class="has-text-centered">
        <span>Transform</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-bottom"
          data-tooltip="Options for data transformation within a scheduled ELT pipeline."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class="has-text-centered">
        <span>Interval</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-left"
          data-tooltip="The frequency of running a scheduled ELT pipeline to get up-to-date data."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th v-if="hasStartDate" class="has-text-centered">
        <span>Start Date</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-left"
          :class="{ 'is-tooltip-left': !hasActions }"
          data-tooltip="The oldest date from which to extract data as part of this scheduled ELT pipeline. Currently, the extractor's Start Date value is used."
        >
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>

      <template v-if="hasActions">
        <th class="has-text-centered">
          <span>Last Run</span>
          <span
            class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-left"
            data-tooltip="The logging status of the last ELT run for this pipeline."
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
