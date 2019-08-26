<script>
import utils from '@/utils/utils'

export default {
  name: 'InputDateIso8601',
  props: {
    value: { type: String, default: '' },
    name: { type: String, default: '' },
    inputClasses: { type: String, default: '' }
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
  <div class="control">
    <input
      :id="`date-${name}`"
      type="date"
      class="input"
      :class="inputClasses"
      :value="formatDateStringYYYYMMDD(value)"
      :name="`date-${name}`"
      :pattern="getInputDateMeta.pattern"
      :min="getInputDateMeta.min"
      :max="getInputDateMeta.today"
      @input="updateValue($event.target.value)"
    />
  </div>
</template>

<style lang="scss"></style>
