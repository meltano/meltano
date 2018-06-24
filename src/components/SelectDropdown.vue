<template>
  <div class="control">
    <div class="dropdown" :class="{'is-active': inputFocused}">
      <div class="dropdown-trigger">
        <input class="input"
            type="email" @focus="inputIsFocused" @blur="inputIsBlurred"
            :placeholder="placeholder">
      </div>
      <div class="dropdown-menu">
        <div class="dropdown-content">
          <a href="#" class="dropdown-item" v-for="item in dropdownList" :key="item.label">
            {{item[dropdownLabelKey]}}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      inputFocused: false,
    };
  },
  props: {
    placeholder: {
      type: String,
      default: 'placeholder',
    },
    dropdownList: {
      type: Array,
      default() {
        return [{ label: 'hello' }];
      },
    },
    dropdownLabelKey: {
      type: String,
      default: 'label',
    },
  },
  methods: {
    inputIsFocused() {
      this.inputFocused = true;
      this.$emit('focused');
    },
    inputIsBlurred() {
      this.inputFocused = false;
      this.$emit('blurred');
    },
  },
};
</script>
