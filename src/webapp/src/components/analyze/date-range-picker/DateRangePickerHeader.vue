<script>
import { mapGetters } from 'vuex'

import {
  getDateLabel,
  getHasValidDateRange
} from '@/components/analyze/date-range-picker/utils'
import DateRangeCustomVsRelative from '@/components/analyze/date-range-picker/DateRangeCustomVsRelative'

export default {
  name: 'DateRangePickerHeader',
  components: {
    DateRangeCustomVsRelative
  },
  props: {
    attributePair: { type: Object, required: true },
    attributePairsModel: { type: Array, required: true }
  },
  computed: {
    ...mapGetters('designs', ['getTableSources']),
    getDateLabel() {
      return getDateLabel
    },
    getHasValidDateRange() {
      return getHasValidDateRange
    },
    getLabel() {
      return targetAttributePair => {
        const attribute = targetAttributePair.attribute
        const source = this.getSourceTableByAttribute(attribute)
        return `${source.label} - ${attribute.label}`
      }
    },
    getSourceTableByAttribute() {
      return attribute =>
        this.getTableSources.find(
          source => source.name === attribute.sourceName
        )
    },
    getValue() {
      return targetAttributePair => {
        const attribute = targetAttributePair.attribute
        return `${attribute.sourceName}.${attribute.name}`
      }
    }
  },
  methods: {
    onChangeAttributePair(option) {
      const value = option.srcElement.selectedOptions[0].value
      const [sourceName, name] = value.split('.')
      const targetAttributePair = this.attributePairsModel.find(
        attributePair =>
          attributePair.attribute.sourceName === sourceName &&
          attributePair.attribute.name === name
      )
      this.$emit('attribute-pair-change', targetAttributePair)
    },
    onClearDateRange() {
      this.$emit('clear-date-range', this.attributePair)
    }
  }
}
</script>

<template>
  <div>
    <div class="mb1r">
      <div class="field">
        <div class="control">
          <span class="select is-fullwidth">
            <select
              :value="getValue(attributePair)"
              :class="{
                'has-text-interactive-secondary':
                  attributePair.attribute.selected
              }"
              @input="onChangeAttributePair($event)"
            >
              <option
                v-for="pair in attributePairsModel"
                :key="getValue(pair)"
                :value="getValue(pair)"
                >{{ getLabel(pair) }}</option
              >
            </select>
          </span>
        </div>
      </div>
    </div>

    <div class="columns is-vcentered">
      <div class="column">
        <DateRangeCustomVsRelative />
      </div>

      <div class="column">
        <div class="is-flex is-vcentered is-pulled-right">
          <span
            class="is-size-7"
            :class="{
              'mr-05r': getHasValidDateRange(attributePair.dateRange)
            }"
            >{{ getDateLabel(attributePair) }}</span
          >
          <button
            v-if="getHasValidDateRange(attributePair.dateRange)"
            class="button is-small"
            @click="onClearDateRange"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
