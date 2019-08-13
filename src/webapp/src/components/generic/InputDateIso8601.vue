<script>
import utils from '@/utils/utils'

export default {
  name: 'InputDateIso8601',
  props: {
    value: { type: String, default: 'null' },
    name: { type: String, required: true, default: '' }
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
      this.$emit('input', `${new Date(val).toISOString().split('.')[0]}Z`)
    }
  }
}
</script>

<template>
  <input
    type="date"
    @input="updateValue($event.target.value)"
    :value="formatDateStringYYYYMMDD(value)"
    :id="`date-${name}`"
    :name="`date-${name}`"
    :pattern="getInputDateMeta.pattern"
    :min="getInputDateMeta.min"
    :max="getInputDateMeta.today"
  />
</template>

<style lang="scss"></style>
