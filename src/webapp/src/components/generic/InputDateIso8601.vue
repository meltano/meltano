<script>
import utils from '@/utils/utils'

export default {
  name: 'InputDateIso8601',
  props: {
    forId: { type: String, default: '' },
    inputClasses: { type: String, default: '' },
    name: { type: String, default: '' },
    value: { type: String, default: '' }
  },
  computed: {
    getInputDateMeta() {
      return utils.getInputDateMeta()
    }
  },
  methods: {
    formatDateStringYYYYMMDD(val) {
      return val && utils.formatDateStringYYYYMMDD(val)
    },
    updateValue(val) {
      this.$emit('input', utils.dateIso8601Nullable(val))
    }
  }
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
      :pattern="getInputDateMeta.pattern"
      :min="getInputDateMeta.min"
      :max="getInputDateMeta.today"
      @input="updateValue($event.target.value)"
    />
  </div>
</template>

<style lang="scss"></style>
