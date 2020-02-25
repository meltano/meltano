<script>
import { mapActions, mapGetters } from 'vuex'

import lodash from 'lodash'

import DateRangePickerHeader from '@/components/analyze/date-range-picker/DateRangePickerHeader'
import Dropdown from '@/components/generic/Dropdown'
import { QUERY_ATTRIBUTE_TYPES } from '@/api/design'
import utils from '@/utils/utils'

export default {
  name: 'DateRangePicker',
  components: {
    DateRangePickerHeader,
    Dropdown
  },
  props: {
    attributes: { type: Array, required: true },
    columnFilters: { type: Array, required: true },
    tableSources: { type: Array, required: true }
  },
  data: () => ({
    attributePairsModel: [],
    attributePairInFocusIndex: 0
  }),
  computed: {
    ...mapGetters('designs', [
      'getAttributesOfDate',
      'getFilters',
      'getIsAttributeInFilters'
    ]),
    getAttributePairInFocus() {
      return this.attributePairsModel[this.attributePairInFocusIndex]
    },
    getAttributePairsInitial() {
      const groupedFilters = lodash.groupBy(this.getDateFilters, 'expression')
      return this.attributes.map(attribute => {
        const finder = filter => {
          return (
            filter.sourceName === attribute.sourceName &&
            filter.name === attribute.name
          )
        }
        let dateRange = { start: null, end: null }
        if (!lodash.isEmpty(groupedFilters)) {
          const start = groupedFilters['greater_or_equal_than'].find(finder)
          const end = groupedFilters['less_or_equal_than'].find(finder)
          dateRange = {
            start: start ? new Date(start.value) : null,
            end: end ? new Date(end.value) : null
          }
        }
        return { attribute, dateRange }
      })
    },
    getDateFilters() {
      return this.columnFilters.filter(filter =>
        this.getAttributesOfDate.find(
          attribute =>
            filter.sourceName === attribute.sourceName &&
            filter.name === attribute.name
        )
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
    getIsAttributePairInFocus() {
      return attributePair =>
        attributePair ===
        this.attributePairsModel[this.attributePairInFocusIndex]
    },
    getIsSavable() {
      const mapper = attributePair => attributePair.dateRange
      const initialDateRanges = this.getAttributePairsInitial.map(mapper)
      const modelDateRanges = this.attributePairsModel.map(mapper)
      return !lodash.isEqual(initialDateRanges, modelDateRanges)
    },
    getKey() {
      return utils.key
    },
    getLabel() {
      const validDateRangeLength = this.getValidDateRangesInitial.length
      const hasValidDateRanges = validDateRangeLength > 0
      let rangeLabel
      if (hasValidDateRanges) {
        rangeLabel = this.getDateLabel(this.getValidDateRangesInitial[0])
        if (validDateRangeLength > 1) {
          rangeLabel += ` (+${validDateRangeLength - 1})`
        }
      }
      return hasValidDateRanges ? rangeLabel : 'Date Ranges'
    },
    getValidDateRangesInitial() {
      return this.getAttributePairsInitial.filter(attributePair =>
        this.getHasValidDateRange(attributePair.dateRange)
      )
    }
  },
  methods: {
    ...mapActions('designs', ['addFilter', 'removeFilter', 'updateFilter']),
    onChangeAttributePairInFocus(attributePair) {
      this.attributePairInFocusIndex = this.attributePairsModel.indexOf(
        attributePair
      )
    },
    onClearDateRange(attributePair) {
      attributePair.dateRange = { start: null, end: null }
    },
    onDropdownOpen() {
      this.attributePairsModel = lodash.cloneDeep(this.getAttributePairsInitial)
    },
    saveDateRanges() {
      this.attributePairsModel.forEach(attributePair => {
        const { attribute, dateRange } = attributePair
        const partialShared = {
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

        // Apply filters as a pair of add|remove|update
        const { name, sourceName } = attribute
        const filters = this.getFilters(
          sourceName,
          name,
          QUERY_ATTRIBUTE_TYPES.COLUMN
        )
        const isAdd = filters.length === 0
        const isNullRange =
          partialStart.value === null && partialEnd.value === null
        if (isAdd && !isNullRange) {
          this.addFilter(Object.assign(partialStart, partialShared))
          this.addFilter(Object.assign(partialEnd, partialShared))
        } else {
          const startFilter = filters.find(
            filter => filter.expression === partialStart.expression
          )
          const endFilter = filters.find(
            filter => filter.expression === partialEnd.expression
          )
          if (isNullRange) {
            this.removeFilter(startFilter)
            this.removeFilter(endFilter)
          } else {
            this.updateFilter({
              filter: startFilter,
              value: partialStart.value
            })
            this.updateFilter({ filter: endFilter, value: partialEnd.value })
          }
        }
      })
    }
  }
}
</script>

<template>
  <Dropdown
    ref="date-range-dropdown"
    :label="getLabel"
    menu-classes="dropdown-menu-600"
    :button-classes="
      `${
        getValidDateRangesInitial.length > 0
          ? 'has-text-interactive-secondary'
          : ''
      }`
    "
    is-right-aligned
    icon-open="calendar"
    @dropdown:open="onDropdownOpen"
  >
    <div class="dropdown-content">
      <!-- Picker Header -->
      <div v-if="getAttributePairInFocus" class="dropdown-item">
        <DateRangePickerHeader
          :attribute-pair="getAttributePairInFocus"
          :attribute-pairs-model="attributePairsModel"
          :get-date-label="getDateLabel"
          :get-has-valid-date-range="getHasValidDateRange"
          :table-sources="tableSources"
          @attribute-pair-change="onChangeAttributePairInFocus"
          @clear-date-range="onClearDateRange"
        />
      </div>

      <!-- Picker Body -->
      <template v-for="attributePair in attributePairsModel">
        <div
          v-if="getIsAttributePairInFocus(attributePair)"
          :key="
            getKey(
              attributePair.attribute.sourceName,
              attributePair.attribute.name
            )
          "
          class="dropdown-item"
        >
          <v-date-picker
            v-model="attributePair.dateRange"
            class="v-calendar-theme"
            mode="range"
            is-expanded
            is-inline
            :columns="2"
          />
        </div>
      </template>

      <!-- Picker Footer -->
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

<style lang="scss">
/* TODO refactor with proper themeing (font and is-interactive-secondary color) when guide is udpated https://vcalendar.io/theming-guide.html */
.v-calendar-theme {
  font-family: $family-sans-serif;
}
</style>
