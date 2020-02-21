<script>
import { mapGetters } from 'vuex'

import lodash from 'lodash'

import Dropdown from '@/components/generic/Dropdown'
import utils from '@/utils/utils'

export default {
  name: 'Bar',
  components: {
    Dropdown
  },
  props: {
    attributes: { type: Array, required: true }
  },
  data: () => ({
    attributePairs: [],
    defaultDateRange: Object.freeze({ start: null, end: null }),
    initialDateRanges: []
  }),
  computed: {
    ...mapGetters('designs', ['getIsAttributeInFilters']),
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
    clearDateRange(attributePair) {
      attributePair.dateRange = this.defaultDateRange
    },
    initializeAttributePairs() {
      this.attributePairs = this.attributes.map(attribute => {
        const dateRange = attribute.dateRange || this.defaultDateRange
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
    saveDateRanges() {}
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
