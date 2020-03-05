<script>
import { EVENTS } from '@/components/analyze/date-range-picker/events'
import { RELATIVE_DATE_RANGE_MODELS } from '@/components/analyze/date-range-picker/utils'
import utils from '@/utils/utils'

export default {
  name: 'DateRangeCustomVsRelative',
  props: {},
  data() {
    return {
      isRelative: false,
      model: {
        number: 7,
        period: RELATIVE_DATE_RANGE_MODELS.PERIODS.DAYS.name,
        sign: RELATIVE_DATE_RANGE_MODELS.SIGNS.LAST.name
      }
    }
  },
  computed: {
    getEmptyDateRange() {
      return { start: null, end: null }
    },
    getPeriods() {
      return RELATIVE_DATE_RANGE_MODELS.PERIODS
    },
    getRelativeDateRange() {
      const relative = `${this.model.sign}${this.model.number} ${this.model.period}`
      console.log(relative)

      // TODO relative map
      const today = new Date()
      const offset = new Date('2020-03-04') // TODO relative map value here
      const isLast =
        this.model.sign === RELATIVE_DATE_RANGE_MODELS.SIGNS.LAST.name
      const start = isLast ? offset : today
      const end = isLast ? today : offset
      return { start, end }
    },
    getSigns() {
      return RELATIVE_DATE_RANGE_MODELS.SIGNS
    }
  },
  methods: {
    emitDateRangeTypeChange() {
      this.$root.$emit(EVENTS.CHANGE_DATE_RANGE_TYPE, {
        isRelative: this.isRelative,
        dateRange: this.isRelative
          ? this.getRelativeDateRange
          : this.getEmptyDateRange
      })
    },
    onIsRelativeChange(value) {
      if (this.isRelative !== value) {
        this.isRelative = value
        this.emitDateRangeTypeChange()
      }
    },
    onChangeRelativeInput() {
      this.emitDateRangeTypeChange()
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
            :class="{ 'is-interactive-secondary is-active': !isRelative }"
            @click="onIsRelativeChange(false)"
          >
            Custom
          </button>
        </div>
        <div class="control">
          <div
            class="button is-small is-outlined tooltip"
            data-tooltip="Date range is relative to today"
            :class="{
              'is-interactive-secondary is-active has-nested-control': isRelative
            }"
            @click="onIsRelativeChange(true)"
          >
            <span>Relative</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isRelative" class="control">
      <div class="field has-addons">
        <div class="control">
          <span class="select is-small">
            <select v-model="model.sign" @change="onChangeRelativeInput">
              <option
                v-for="(sign, key) in getSigns"
                :key="key"
                :value="sign.name"
                >{{ sign.label }}</option
              >
            </select>
          </span>
        </div>
        <div class="control">
          <input
            v-model="model.number"
            class="input is-small max-width-3r"
            type="number"
            min="1"
            @change="onChangeRelativeInput"
          />
        </div>
        <div class="control">
          <span class="select is-small">
            <select v-model="model.period" @change="onChangeRelativeInput">
              <option
                v-for="(period, key) in getPeriods"
                :key="key"
                :value="period.name"
                >{{ period.label }}</option
              >
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
