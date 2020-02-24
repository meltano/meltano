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
    attributePairsModel: []
  }),
  computed: {
    ...mapGetters('designs', [
      'getAttributesOfDate',
      'getFilters',
      'getIsAttributeInFilters'
    ]),
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
    clearDateRange(attributePair) {
      attributePair.dateRange.start = null
      attributePair.dateRange.end = null
    },
    onDropdownClose() {},
    onDropdownOpen() {
      this.attributePairsModel = lodash.cloneDeep(this.getAttributePairsInitial)
    },
    onSelectDateRange() {},
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
        if (filters.length) {
          const startFilter = filters.find(
            filter => filter.expression === partialStart.expression
          )
          const endFilter = filters.find(
            filter => filter.expression === partialEnd.expression
          )
          const isRemove = partialStart.value === null
          if (isRemove) {
            this.removeFilter(startFilter)
            this.removeFilter(endFilter)
          } else {
            this.updateFilter({
              filter: startFilter,
              value: partialStart.value
            })
            this.updateFilter({ filter: endFilter, value: partialEnd.value })
          }
        } else {
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
    @dropdown:close="onDropdownClose"
  >
    <div class="dropdown-content">
      <div
        v-for="attributePair in attributePairsModel"
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
