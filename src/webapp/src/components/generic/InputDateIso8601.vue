<script>
import utils from '@/utils/utils'

export default {
  name: 'InputDateIso8601',
  props: {
    forId: { type: String, default: '' },
    inputClasses: { type: String, default: '' },
    disabled: { type: Boolean, default: false },
    name: { type: String, default: '' },
    value: { type: String, default: '' },
  },
  computed: {
    getInputDateMeta() {
      return utils.getInputDateMeta()
    },
  },
  methods: {
    formatDateStringYYYYMMDD(val) {
      if (!val) {
        return null
      }

      // Depending on what was saved before, val may either hold a
      // YYYY-MM-DD date string or a full ISO8601 timestamp string.
      // We always need a YYYY-MM-DD date string, so let's convert.
      const date = utils.getDateFromYYYYMMDDString(val)
      return utils.formatDateStringYYYYMMDD(date)
    },
    updateValue(val) {
      // Val is already formatted as YYYY-MM-DD
      this.$emit('input', val || null)
    },
  },
}
</script>

<template>
  <div class="control">
    <input
      :id="forId || `date-${name}`"
      type="date"
      class="input"
      :class="inputClasses"
      :value="formatDateStringYYYYMMDD(value)"
      :name="forId || `date-${name}`"
      :disabled="disabled"
      :pattern="getInputDateMeta.pattern"
      :min="getInputDateMeta.min"
      :max="getInputDateMeta.today"
      @input="updateValue($event.target.value)"
    />
  </div>
</template>

<style lang="scss"></style>
