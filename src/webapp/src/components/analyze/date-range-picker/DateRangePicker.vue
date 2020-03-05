<script>
import { mapActions, mapGetters } from 'vuex'

import lodash from 'lodash'

import DateRangePickerHeader from '@/components/analyze/date-range-picker/DateRangePickerHeader'
import Dropdown from '@/components/generic/Dropdown'
import { EVENTS } from '@/components/analyze/date-range-picker/events'
import {
  getDateLabel,
  getHasValidDateRange
} from '@/components/analyze/date-range-picker/utils'
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
    columnFilters: { type: Array, required: true }
  },
  data: () => ({
    attributePairsModel: [],
    attributePairInFocusIndex: 0
  }),
  computed: {
    ...mapGetters('designs', [
      'getFilters',
      'getIsAttributeInFilters',
      'getIsDateAttribute'
    ]),
    getAttributePairInFocus() {
      return this.attributePairsModel[this.attributePairInFocusIndex]
    },
    getAttributePairsInitial() {
      return this.attributes.map(attribute => {
        const filters = this.getFiltersForAttribute(attribute)
        const start = filters.find(
          filter => filter.expression === 'greater_or_equal_than'
        )
        const end = filters.find(
          filter => filter.expression === 'less_or_equal_than'
        )
        const dateRange = {
          start: start ? utils.getDateFromYYYYMMDDString(start.value) : null,
          end: end ? utils.getDateFromYYYYMMDDString(end.value) : null
        }
        return { attribute, dateRange }
      })
    },
    getDateFilters() {
      return this.columnFilters.filter(filter =>
        this.getIsDateAttribute(filter.attribute)
      )
    },
    getDateLabel() {
      return getDateLabel
    },
    getHasValidDateRange() {
      return getHasValidDateRange
    },
    getFiltersForAttribute() {
      return attribute =>
        this.getFilters(
          attribute.sourceName,
          attribute.name,
          QUERY_ATTRIBUTE_TYPES.COLUMN
        )
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
  created() {
    this.$root.$on(EVENTS.CHANGE_DATE_RANGE_TYPE, this.onChangeDateRangeType)
  },
  methods: {
    ...mapActions('designs', ['addFilter', 'removeFilter']),
    onChangeAttributePairInFocus(attributePair) {
      this.attributePairInFocusIndex = this.attributePairsModel.indexOf(
        attributePair
      )
    },
    onClearDateRange(attributePair) {
      attributePair.dateRange = { start: null, end: null }
    },
    onChangeDateRangeType(payload) {
      const attributePairInFocus = this.getAttributePairInFocus
      attributePairInFocus.dateRange = payload.dateRange
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

        let startValue = dateRange.start || null
        if (startValue) {
          startValue = utils.formatDateStringYYYYMMDD(startValue)
          if (attribute.type === 'time') {
            startValue += 'T00:00:00.000Z'
          }
        }
        let endValue = dateRange.end || null
        if (endValue) {
          endValue = utils.formatDateStringYYYYMMDD(endValue)
          if (attribute.type === 'time') {
            endValue += 'T23:59:59.999Z'
          }
        }

        const partialStart = {
          expression: 'greater_or_equal_than', // TODO refactor `filterOptions` and/or constants approach
          value: startValue
        }
        const partialEnd = {
          expression: 'less_or_equal_than', // TODO refactor `filterOptions` and/or constants approach
          value: endValue
        }

        // Apply filters as a pair
        const filters = this.getFiltersForAttribute(attribute)
        const startFilter = filters.find(
          filter => filter.expression === partialStart.expression
        )
        const endFilter = filters.find(
          filter => filter.expression === partialEnd.expression
        )

        // Always remove before conditionally adding for simplicity (removes need for an `updateFilter()` at negligable perf cost)
        const hasFilters = filters.length > 0
        if (hasFilters) {
          this.removeFilter(startFilter)
          this.removeFilter(endFilter)
        }

        const isAdd = partialStart.value !== null && partialEnd.value !== null
        if (isAdd) {
          this.addFilter(Object.assign(partialStart, partialShared))
          this.addFilter(Object.assign(partialEnd, partialShared))
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
