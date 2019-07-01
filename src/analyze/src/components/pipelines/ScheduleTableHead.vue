<script>

export default {
  name: 'ScheduleTableHead',
  props: {
    hasActions: { type: Boolean, default: false },
  },
};
</script>

<template>

  <thead>
    <tr>
      <th>
        <span>Name</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-right"
          data-tooltip="The unique identifier for a schedule and its settings.">
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class='has-text-centered'>
        <span>Extractor</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline"
          data-tooltip='The connector for data extraction within a scheduled ELT pipeline.'>
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class='has-text-centered'>
        <span>Loader</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline"
          data-tooltip='The connector for data loading within a scheduled ELT pipeline.'>
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class='has-text-centered'>
        <span>Transform</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline"
          data-tooltip='Options for data transformation within a scheduled ELT pipeline.'>
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class='has-text-centered'>
        <span>Interval</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline"
          data-tooltip='The frequency of running a scheduled ELT pipeline to get up-to-date data.'>
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>
      <th class='has-text-centered'>
        <span>Catch-up Date</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline"
          :class="{ 'is-tooltip-left': !hasActions }"
          data-tooltip="The oldest date from which to extract data as part of this scheduled ELT pipeline. 'None' uses the Extractor's default Start Date.">
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>

      <th
        v-if='hasActions'
        class='has-text-centered'>
        <span>Actions</span>
        <span
          class="icon has-text-grey-light tooltip is-tooltip-multiline is-tooltip-left"
          data-tooltip="Steps to take with a given ELT pipeline schedule.">
          <font-awesome-icon icon="info-circle"></font-awesome-icon>
        </span>
      </th>

    </tr>
  </thead>

</template>

<style lang="scss">
</style>
