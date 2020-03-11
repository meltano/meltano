<script>
import moment from 'moment'

import { EVENTS } from '@/components/analyze/date-range-picker/events'
import {
  getIsRelativeLast,
  getNullDateRange,
  getRelativeOffsetFromDateRange,
  getRelativeSignNumberPeriod,
  RELATIVE_DATE_RANGE_MODELS
} from '@/components/analyze/date-range-picker/utils'

export default {
  name: 'DateRangeCustomVsRelative',
  props: {
    attributePair: { type: Object, required: true }
  },
  data() {
    return {
      model: {
        number: 7,
        period: RELATIVE_DATE_RANGE_MODELS.PERIODS.DAYS.NAME,
        sign: RELATIVE_DATE_RANGE_MODELS.SIGNS.LAST.NAME
      }
    }
  },
  computed: {
    getIsLast() {
      return getIsRelativeLast(this.model.sign)
    },
    getIsPeriodDisabled() {
      return period => period.IS_DISABLED
    },
    getPeriods() {
      return RELATIVE_DATE_RANGE_MODELS.PERIODS
    },
    getAbsoluteDateRange() {
      const method = this.getIsLast ? 'subtract' : 'add'
      const momentAnchor = moment()[method](1, 'days')
      const anchor = momentAnchor.toDate()
      const momentOffset = moment()[method](
        this.model.number,
        this.model.period
      )
      const offset = momentOffset.toDate()
      return this.getDateRange(anchor, offset)
    },
    getDateRange() {
      return (anchor, offset) => {
        const start = this.getIsLast ? offset : anchor
        const end = this.getIsLast ? anchor : offset
        return { start, end }
      }
    },
    getSigns() {
      return RELATIVE_DATE_RANGE_MODELS.SIGNS
    },
    getRelativeDateRange() {
      const anchor = `${this.model.sign}1${this.model.period}`
      const offset = `${this.model.sign}${this.model.number}${this.model.period}`
      return this.getDateRange(anchor, offset)
    }
  },
  watch: {
    attributePair: function(val) {
      this.setModel(val.relativeDateRange)
    }
  },
  created() {
    this.setModel(this.attributePair.relativeDateRange)
  },
  methods: {
    emitChangeDateRange(value) {
      const isRelative = value
      const relativeDateRange = isRelative
        ? this.getRelativeDateRange
        : getNullDateRange()
      const absoluteDateRange = isRelative
        ? this.getAbsoluteDateRange
        : getNullDateRange()
      const payload = { isRelative, relativeDateRange, absoluteDateRange }
      this.$root.$emit(EVENTS.CHANGE_DATE_RANGE, payload)
    },
    onChangeRelativeInput() {
      this.emitChangeDateRange(true)
    },
    onIsRelativeChange(value) {
      if (this.attributePair.isRelative !== value) {
        this.emitChangeDateRange(value)
      }
    },
    setModel(dateRange) {
      if (dateRange.start && dateRange.end) {
        const offset = getRelativeOffsetFromDateRange(dateRange)
        this.model = getRelativeSignNumberPeriod(offset)
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
            :class="{
              'is-interactive-secondary is-active': !attributePair.isRelative
            }"
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
              'is-interactive-secondary is-active has-nested-control':
                attributePair.isRelative
            }"
            @click="onIsRelativeChange(true)"
          >
            <span>Relative</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="attributePair.isRelative" class="control">
      <div class="field has-addons">
        <div class="control">
          <span class="select is-small">
            <select v-model="model.sign" @change="onChangeRelativeInput">
              <option
                v-for="(sign, key) in getSigns"
                :key="key"
                :value="sign.NAME"
                >{{ sign.LABEL }}</option
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
                :value="period.NAME"
                :disabled="getIsPeriodDisabled(period)"
                >{{ period.LABEL }}</option
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
