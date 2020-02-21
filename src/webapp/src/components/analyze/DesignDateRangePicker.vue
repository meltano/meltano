<script>
import { mapGetters } from 'vuex'

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
    attributePairs: []
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
      return false
    },
    getKey() {
      return utils.key
    }
  },
  methods: {
    clearDateRange(attributePair) {
      attributePair.dateRange = { start: null, end: null }
    },
    onDropdownOpen() {
      this.processAttributePairs()
    },
    onSelectDateRange() {},
    processAttributePairs() {
      this.attributePairs = this.attributes.map(attribute => {
        return { attribute, dateRange: { start: null, end: null } }
      })
    },
    saveDateRanges() {}
  }
}
</script>

<template>
  <Dropdown
    label="Date Ranges"
    menu-classes="dropdown-menu-600"
    is-right-aligned
    icon-open="calendar"
    @dropdown:open="onDropdownOpen"
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
            <div class="is-pulled-right">
              <span>{{ getDateLabel(attributePair) }}</span>
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
          :max-date="new Date()"
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
