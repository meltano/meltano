<script>
export default {
  name: 'DateRangePickerHeader',
  props: {
    attributePairInFocus: { type: Object, required: true },
    attributePairsModel: { type: Array, required: true },
    getDateLabel: { type: Function, required: true },
    getHasValidDateRange: { type: Function, required: true }
  },
  methods: {
    onChangeAttributePairInFocus(option) {
      this.$emit('attribute-pair-change', option)
    },
    onClearDateRange() {
      this.$emit('clear-date-range', this.attributePairInFocus)
    }
  }
}
</script>

<template>
  <div class="columns is-vcentered">
    <div class="column">
      <div class="field">
        <div class="control">
          <span class="select">
            <select
              :value="attributePairInFocus.attribute.label"
              :class="{
                'has-text-interactive-secondary':
                  attributePairInFocus.attribute.selected
              }"
              @input="onChangeAttributePairInFocus($event)"
            >
              <option
                v-for="pair in attributePairsModel"
                :key="pair.attribute.label"
                :value="pair.attribute.label"
                >{{ pair.attribute.label }}</option
              >
            </select>
          </span>
        </div>
      </div>
    </div>

    <div class="column">
      <div class="is-flex is-vcentered is-pulled-right">
        <span
          :class="{
            'mr-05r': getHasValidDateRange(attributePairInFocus.dateRange)
          }"
          >{{ getDateLabel(attributePairInFocus) }}</span
        >
        <button
          v-if="getHasValidDateRange(attributePairInFocus.dateRange)"
          class="button is-small"
          @click="onClearDateRange"
        >
          Clear
        </button>
      </div>
    </div>
  </div>
</template>

<style lang="scss"></style>
