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
    dateRange: { start: null, end: null }
  }),
  computed: {
    ...mapGetters('designs', ['getIsAttributeInFilters']),
    key() {
      return utils.key
    }
  },
  methods: {
    onSelectDateRange(data) {
      console.log('hit', data)
    },
    saveDateRanges() {}
  }
}
</script>

<template>
  <Dropdown
    label="No Date Filtering Applied"
    menu-classes="dropdown-menu-600"
    is-right-aligned
    icon-open="calendar"
  >
    <div class="dropdown-content">
      <div
        v-for="attribute in attributes"
        :key="key(attribute.name)"
        class="dropdown-item"
      >
        <div class="columns is-vcentered is-marginless">
          <div class="column">
            <label
              class="label has-text-weight-medium"
              :class="{ 'has-text-interactive-secondary': attribute.selected }"
              >{{ attribute.label }}</label
            >
          </div>
          <div class="column">
            <span class="is-pulled-right">None</span>
          </div>
        </div>
        <v-date-picker
          v-model="dateRange"
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
