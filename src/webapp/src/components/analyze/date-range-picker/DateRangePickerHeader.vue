<script>
export default {
  name: 'DateRangePickerHeader',
  props: {
    attributePair: { type: Object, required: true },
    attributePairsModel: { type: Array, required: true },
    getDateLabel: { type: Function, required: true },
    getHasValidDateRange: { type: Function, required: true },
    tableSources: { type: Array, required: true }
  },
  computed: {
    getLabel() {
      return targetAttributePair => {
        const attribute = targetAttributePair.attribute
        const source = this.getSourceTableByAttribute(attribute)
        return `${source.tableLabel} - ${attribute.label}`
      }
    },
    getSourceTableByAttribute() {
      return attribute =>
        this.tableSources.find(
          source => source.sourceName === attribute.sourceName
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
  <div class="columns is-vcentered">
    <div class="column">
      <div class="field">
        <div class="control">
          <span class="select is-small">
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
</template>

<style lang="scss"></style>
