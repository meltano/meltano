<script>
import { mapGetters } from 'vuex'
import lodash from 'lodash'

import { selected } from '@/utils/predicates'

export const TABLE_ATTRIBUTE_TYPES = Object.freeze({
  COLUMN: 'column',
  AGGREGATE: 'aggregate',
  TIMEFRAME: 'timeframe'
})

export default {
  name: 'TableAttributeButton',
  props: {
    attribute: { type: Object, required: true },
    attributeType: {
      type: String,
      required: true,
      validator: value => Object.values(TABLE_ATTRIBUTE_TYPES).includes(value)
    },
    design: { type: Object, required: true } // The base table's design or the design of a join table (`.name` and `.relatedTable` use)
  },
  computed: {
    ...mapGetters('designs', ['getIsAttributeInFilters']),
    getIsActive() {
      return this.getIsTimeframe
        ? this.getIsTimeframeSelected
        : this.attribute.selected
    },
    getIsTimeframe() {
      return this.attributeType === TABLE_ATTRIBUTE_TYPES.TIMEFRAME
    },
    getIsTimeframeSelected() {
      const hasSelectedPeriods = lodash.some(this.attribute.periods, selected)
      return this.attribute.selected || hasSelectedPeriods
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
    class="panel-block panel-block-button button is-small space-between has-text-weight-medium"
    :class="{
      'is-active': getIsActive,
      timeframe: getIsTimeframe
    }"
    @click="onAttributeSelected"
  >
    {{ attribute.label }}
    <button
      v-if="getIsAttributeInFilters(design.name, attribute.name, attributeType)"
      class="button is-small"
      @click.stop="onFilterClick"
    >
      <span class="icon has-text-interactive-secondary">
        <font-awesome-icon icon="filter"></font-awesome-icon>
      </span>
    </button>
  </button>
</template>

<style lang="scss"></style>
