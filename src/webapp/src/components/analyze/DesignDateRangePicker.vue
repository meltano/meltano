<script>
import { mapActions, mapGetters } from 'vuex'

import lodash from 'lodash'

import Dropdown from '@/components/generic/Dropdown'
import { QUERY_ATTRIBUTE_TYPES } from '@/api/design'
import utils from '@/utils/utils'

export default {
  name: 'DesignDateRangePicker',
  components: {
    Dropdown
  },
  props: {
    attributes: { type: Array, required: true },
    columnFilters: { type: Array, required: true }
  },
  data: () => ({
    attributePairs: [],
    defaultDateRange: Object.freeze({ start: null, end: null }),
    initialDateRanges: []
  }),
  computed: {
    ...mapGetters('designs', [
      'getAttributesOfDate',
      'getIsAttributeInFilters'
    ]),
    getDateFilters() {
      return this.columnFilters.filter(filter =>
        this.getAttributesOfDate.includes(filter.attribute)
      )
    },
    getDateLabel() {
      return attributePair => {
        return this.getHasValidDateRange(attributePair.dateRange)
          ? `${utils.formatDateStringYYYYMMDD(
              attributePair.dateRange.start
            )} - ${utils.formatDateStringYYYYMMDD(attributePair.dateRange.end)}`
          : 'None'
      }
    },
    getHasValidDateRange() {
      return dateRange => dateRange.start && dateRange.end
    },
    getIsSavable() {
      const dateRanges = this.attributePairs.map(
        attributePair => attributePair.dateRange
      )
      return !lodash.isEqual(dateRanges, this.initialDateRanges)
    },
    getKey() {
      return utils.key
    },
    getLabel() {
      const validDateRangeLength = this.getValidDateRanges.length
      const hasValidDateRanges = validDateRangeLength > 0
      let rangeLabel
      if (hasValidDateRanges) {
        rangeLabel = this.getDateLabel(this.getValidDateRanges[0])
        if (validDateRangeLength > 1) {
          rangeLabel += ` (+${validDateRangeLength - 1})`
        }
      }
      return hasValidDateRanges ? rangeLabel : 'Date Ranges'
    },
    getValidDateRanges() {
      return this.attributePairs.filter(attributePair =>
        this.getHasValidDateRange(attributePair.dateRange)
      )
    }
  },
  methods: {
    ...mapActions('designs', ['addFilter', 'removeFilter']),
    clearDateRange(attributePair) {
      attributePair.dateRange = this.defaultDateRange
    },
    initializeAttributePairs() {
      const groupedFilters = lodash.groupBy(this.getDateFilters, 'expression')
      this.attributePairs = this.attributes.map(attribute => {
        const finder = filter => filter.attribute === attribute
        let dateRange = this.defaultDateRange
        if (!lodash.isEmpty(groupedFilters)) {
          const start = groupedFilters['greater_or_equal_than'].find(finder)
            .value
          const end = groupedFilters['less_or_equal_than'].find(finder).value
          dateRange = { start, end }
        }
        return { attribute, dateRange }
      })
    },
    onDropdownClose() {},
    onDropdownOpen() {
      this.initializeAttributePairs()
      this.initialDateRanges = Object.freeze(
        lodash.cloneDeep(
          this.attributePairs.map(attributePair => attributePair.dateRange)
        )
      )
    },
    onSelectDateRange() {},
    saveDateRanges() {
      this.attributePairs.forEach(attributePair => {
        const { attribute, dateRange } = attributePair
        const partialShared = {
          sourceName: attribute.sourceName,
          attribute: attribute,
          filterType: QUERY_ATTRIBUTE_TYPES.COLUMN
        }
        const partialStart = {
          expression: 'greater_or_equal_than', // TODO refactor `filterOptions` and/or constants approach
          value: dateRange.start
        }
        const partialEnd = {
          expression: 'less_or_equal_than', // TODO refactor `filterOptions` and/or constants approach
          value: dateRange.end
        }
        // Add filters as pair
        this.addFilter(Object.assign(partialStart, partialShared))
        this.addFilter(Object.assign(partialEnd, partialShared))
      })
    }
  }
}
</script>

<template>
  <Dropdown
    :label="getLabel"
    menu-classes="dropdown-menu-600"
    :button-classes="
      `${getValidDateRanges.length > 0 ? 'has-text-interactive-secondary' : ''}`
    "
    is-right-aligned
    icon-open="calendar"
    @dropdown:open="onDropdownOpen"
    @dropdown:close="onDropdownClose"
  >
    <div class="dropdown-content">
      <div
        v-for="attributePair in attributePairs"
        :key="getKey(attributePair.attribute.name)"
        class="dropdown-item"
      >
        <div class="columns is-vcentered is-marginless">
          <div class="column">
            <label
              class="label has-text-weight-medium"
              :class="{
                'has-text-interactive-secondary':
                  attributePair.attribute.selected
              }"
              >{{ attributePair.attribute.label }}</label
            >
          </div>
          <div class="column">
            <div class="is-flex is-vcentered is-pulled-right">
              <span
                :class="{
                  'mr-05r': getHasValidDateRange(attributePair.dateRange)
                }"
                >{{ getDateLabel(attributePair) }}</span
              >
              <button
                v-if="getHasValidDateRange(attributePair.dateRange)"
                class="button is-small"
                @click="clearDateRange(attributePair)"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
        <v-date-picker
          v-model="attributePair.dateRange"
          mode="range"
          is-expanded
          is-inline
          :columns="2"
          @input="onSelectDateRange"
        />
      </div>
      <div class="dropdown-item">
        <div class="buttons is-right">
          <button class="button is-text" data-dropdown-auto-close>
            Cancel
          </button>
          <button
            class="button"
            :disabled="!getIsSavable"
            data-dropdown-auto-close
            @click="saveDateRanges"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </Dropdown>
</template>

<style lang="scss"></style>
