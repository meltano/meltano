<script>
import utils from '@/utils/utils';

export default {
  name: 'InputDateIso8601',
  props: {
    value: { type: String, default: '' },
    name: { type: String, required: true, default: '' },
    inputClasses: { type: String },
  },
  computed: {
    getInputDateMeta() {
      return utils.getInputDateMeta();
    },
  },
  methods: {
    formatDateStringYYYYMMDD(val) {
      return val && utils.formatDateStringYYYYMMDD(val);
    },
    updateValue(val) {
      this.$emit('input', `${new Date(val).toISOString().split('.')[0]}Z`);
    },
  },
};
</script>

<template>
<div class="control">
  <input
    type="date"
    class="input"
    :class="inputClasses"
    @input="updateValue($event.target.value)"
    :value="formatDateStringYYYYMMDD(value)"
    :id="`date-${name}`"
    :name="`date-${name}`"
    :pattern="getInputDateMeta.pattern"
    :min='getInputDateMeta.min'
    :max='getInputDateMeta.today'>
  </div>
</template>

<style lang="scss">
</style>
