<script>
import { mapGetters } from 'vuex'
import lodash from 'lodash'

import { QUERY_ATTRIBUTE_TYPES } from '@/api/design'
import { selected } from '@/utils/predicates'

export default {
  name: 'TableAttributeButton',
  props: {
    attribute: { type: Object, required: true },
    attributeType: {
      type: String,
      required: true,
      validator: value => Object.values(QUERY_ATTRIBUTE_TYPES).includes(value)
    },
    design: { type: Object, required: true }, // The base table's design or the design of a join table (`.name` and `.relatedTable` use)
    isDisabled: { type: Boolean, required: false }
  },
  computed: {
    ...mapGetters('designs', ['getIsAttributeInFilters', 'getIsDateAttribute']),
    getHasSelectedPeriods() {
      return (
        this.getIsTimeframe && lodash.some(this.attribute.periods, selected)
      )
    },
    getIsActive() {
      return this.getIsTimeframe
        ? this.attribute.selected || this.getHasSelectedPeriods
        : this.attribute.selected
    },
    getIsColumn() {
      return this.attributeType === QUERY_ATTRIBUTE_TYPES.COLUMN
    },
    getIsTimeframe() {
      return this.attributeType === QUERY_ATTRIBUTE_TYPES.TIMEFRAME
    },
    getFilterIcon() {
      return this.getIsDateAttribute(this.attribute) ? 'calendar' : 'filter'
    },
    getFilterTooltip() {
      const label = this.getIsDateAttribute(this.attribute)
        ? 'Date Ranges'
        : 'Filters'
      return `Jump to ${label}`
    },
    getTimeframeIcon() {
      return `chevron-${this.attribute.selected ? 'up' : 'down'}`
    }
  },
  methods: {
    onAttributeSelected() {
      this.$emit('attribute-selected')
    },
    onFilterClick() {
      const eventName = this.getIsDateAttribute(this.attribute)
        ? 'calendar-click'
        : 'filter-click'
      this.$emit(eventName)
    }
  }
}
</script>

<template>
  <button
    class="panel-block panel-block-button button is-small is-fullwidth space-between has-text-weight-medium"
    :class="{
      'is-active': getIsActive,
      'tooltip is-tooltip-right': attribute.required
    }"
    data-tooltip="This column is required to generate the intended results"
    :disabled="isDisabled"
    @click="onAttributeSelected"
  >
    <!-- Left side of space-between -->
    <span>{{ attribute.label }}</span>

    <!-- Right side of space-between -->
    <div class="is-flex is-vcentered">
      <!-- Timeframe -->
      <div v-if="getIsTimeframe" class="mr-05r">
        <span
          class="icon"
          :class="{ 'has-text-interactive-secondary': getIsActive }"
        >
          <font-awesome-icon :icon="getTimeframeIcon"></font-awesome-icon>
        </span>
      </div>
      <!-- Column or Aggregate -->
      <template v-else>
        <!-- Disabled -->
        <div v-if="isDisabled" class="mr-05r">
          <span class="icon">
            <font-awesome-icon icon="lock"></font-awesome-icon>
          </span>
        </div>
        <!-- Filter -->
        <button
          v-if="getIsAttributeInFilters(attribute)"
          class="button is-small tooltip is-tooltip-right"
          :data-tooltip="getFilterTooltip"
          @click.stop="onFilterClick"
        >
          <span class="icon has-text-interactive-secondary">
            <font-awesome-icon :icon="getFilterIcon"></font-awesome-icon>
          </span>
        </button>
      </template>
    </div>
  </button>
</template>

<style lang="scss">
.panel-block {
  &.space-between {
    justify-content: space-between;
  }

  &.panel-block-button {
    height: auto;
    border-top: 0;
    border-bottom: 1px solid $grey-lighter;
    border-right: 1px solid $grey-lighter;
    border-radius: 0;

    &:disabled {
      // Override to ensure the tooltip doesn't drop opacity. Additionally we use the lock icon.
      opacity: 1;
    }

    &:focus:not(.is-active) {
      border-color: $grey-lighter;
      outline: none;
    }

    &:hover {
      background-color: $white-ter;
    }
  }
}
</style>
