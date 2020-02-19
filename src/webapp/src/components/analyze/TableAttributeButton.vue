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
    design: { type: Object, required: true } // The base table's design or the design of a join table (`.name` and `.relatedTable` use)
  },
  computed: {
    ...mapGetters('designs', ['getIsAttributeInFilters']),
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
    getIsTimeframe() {
      return this.attributeType === QUERY_ATTRIBUTE_TYPES.TIMEFRAME
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
      this.$emit('filter-click')
    }
  }
}
</script>

<template>
  <button
    class="panel-block panel-block-button button is-small is-fullwidth space-between has-text-weight-medium"
    :class="{ 'is-active': getIsActive }"
    @click="onAttributeSelected"
  >
    {{ attribute.label }}

    <!-- Timeframe vs. Column or Aggregate -->
    <div v-if="getIsTimeframe" class="mr-025r">
      <span
        class="icon"
        :class="{ 'has-text-interactive-secondary': getIsActive }"
      >
        <font-awesome-icon :icon="getTimeframeIcon"></font-awesome-icon>
      </span>
    </div>
    <template v-else>
      <button
        v-if="
          getIsAttributeInFilters(design.name, attribute.name, attributeType)
        "
        class="button is-small"
        @click.stop="onFilterClick"
      >
        <span class="icon has-text-interactive-secondary">
          <font-awesome-icon icon="filter"></font-awesome-icon>
        </span>
      </button>
    </template>
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
    border-bottom: 1px solid #dbdbdb;
    border-right: 1px solid #dbdbdb;
    border-radius: 0;

    &:hover {
      background-color: $white-ter;
    }
  }
}
</style>
