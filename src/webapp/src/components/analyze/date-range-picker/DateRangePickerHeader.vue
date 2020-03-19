<script>
import { mapGetters } from 'vuex'

import { EVENTS } from '@/components/analyze/date-range-picker/events'
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
    getHasValidDateRange() {
      return getHasValidDateRange
    },
    getHasMultipleDateRanges() {
      return this.attributePairsModel.length > 1
    },
    getLabel() {
      return targetAttributePair => {
        const attribute = targetAttributePair.attribute
        const source = this.getSourceTableByAttribute(attribute)
        let label = `${source.label} - ${attribute.label}`

        if (targetAttributePair.absoluteDateRange.start !== null) {
          const dateLabel = getDateLabel(targetAttributePair)
          label += ` (${dateLabel})`
        }

        return label
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
        return targetAttributePair.attribute.key
      }
    }
  },
  methods: {
    onChangeAttributePair(option) {
      const key = option.srcElement.selectedOptions[0].value
      const targetAttributePair = this.attributePairsModel.find(
        attributePair => attributePair.attribute.key === key
      )
      this.$emit(EVENTS.ATTRIBUTE_PAIR_CHANGE, targetAttributePair)
    },
    onClearDateRange() {
      this.$emit(EVENTS.CLEAR_DATE_RANGE, this.attributePair)
    }
  }
}
</script>

<template>
  <div>
    <div class="mb1r">
      <div class="field">
        <div class="control">
          <span v-if="getHasMultipleDateRanges" class="select is-fullwidth">
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
          <span v-else>{{ getLabel(attributePairsModel[0]) }}</span>
        </div>
      </div>
    </div>

    <div class="columns is-vcentered">
      <div class="column">
        <DateRangeCustomVsRelative :attribute-pair="attributePair" />
      </div>

      <div class="column">
        <div class="is-flex is-vcentered is-pulled-right">
          <button
            v-if="getHasValidDateRange(attributePair.absoluteDateRange)"
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
