<script>
import { EVENTS } from '@/components/analyze/date-range-picker/events'

export default {
  name: 'DateRangeCustomVsRelative',
  props: {},
  data() {
    return {
      isCustom: true
    }
  },
  computed: {
    getValue() {
      // TODO parse input combo to to a start and end pair
      return new Date()
    }
  },
  methods: {
    emitDateRangeTypeChange() {
      this.$root.$emit(EVENTS.CHANGE_DATE_RANGE_TYPE, {
        isCustom: this.isCustom,
        value: this.getValue
      })
    },
    onIsCustomChange(value) {
      if (this.isCustom !== value) {
        this.isCustom = value
        this.emitDateRangeTypeChange()
      }
    }
  }
}
</script>

<template>
  <div class="field is-grouped">
    <div class="control">
      <div class="field has-addons">
        <div class="control">
          <button
            class="button is-small is-outlined tooltip"
            data-tooltip="Date range is absolute"
            :class="{ 'is-interactive-secondary is-active': isCustom }"
            @click="onIsCustomChange(true)"
          >
            Custom
          </button>
        </div>
        <div class="control">
          <div
            class="button is-small is-outlined tooltip"
            data-tooltip="Date range is relative to today"
            :class="{
              'is-interactive-secondary is-active has-nested-control': !isCustom
            }"
            @click="onIsCustomChange(false)"
          >
            <span>Relative</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!isCustom" class="control">
      <div class="field has-addons">
        <div class="control">
          <span class="select is-small">
            <select value="Past">
              <option>Last</option>
              <option>Next</option>
            </select>
          </span>
        </div>
        <div class="control">
          <input
            class="input is-small max-width-3r"
            type="number"
            min="1"
            value="7"
          />
        </div>
        <div class="control">
          <span class="select is-small">
            <select value="Days">
              <option>Days</option>
              <option>Months</option>
              <option>Years</option>
            </select>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.max-width-3r {
  max-width: 3rem;
}
</style>
