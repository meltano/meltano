<template>
  <div class="columns">
    <div class="column is-6">
      <div class="control is-expanded">
        <div class="select is-fullwidth">
          <select @change="modifierChanged"
                  @focus="modifierFocused"
                  v-model="modifier">
            <option value="" disabled selected>Select modifier</option>
            <option value="equal">is equal to</option>
            <option value="contains">contains</option>
          </select>
        </div>
      </div>
    </div>
    <div class="column is-6">
      <div class="control is-expanded">
        <div class="dropdown" :class="{'is-active': inputFocused}">
          <div class="dropdown-trigger">
            <input class="input is-fullwidth"
                type="email"
                v-model="inputSelection"
                @focus="inputIsFocused"
                @blur="inputIsBlurred"
                @keydown.13="enterPressed"
                :placeholder="placeholder">
          </div>
          <div class="dropdown-menu">
            <div class="dropdown-content">
              <a class="dropdown-item"
                  v-for="item in dropdownList"
                  :key="item.label"
                  @click="dropdownClicked(item)">
                {{item[dropdownLabelKey]}}
              </a>
            </div>
          </div>
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
      modifier: '',
      inputSelection: '',
    };
  },
  props: {
    placeholder: {
      type: String,
      default: 'placeholder',
    },
    field: {
      type: String,
    },
    dropdownList: {
      type: Array,
      default() {
        return [{ label: 'Loading...' }];
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
    inputIsBlurred(e) {
      // FIXME: This is not a good solution.
      // Blur fires before menu closes ¯\_(ツ)_/¯
      e.preventDefault();
      setTimeout(() => {
        this.inputFocused = false;
        this.$emit('blurred');
      }, 200);
    },
    dropdownClicked(item) {
      this.inputFocused = false;
      this.$emit('blurred');
      this.$emit('selected', item[this.dropdownLabelKey], this.field);
    },
    modifierFocused() {
      this.$emit('focused');
    },
    modifierChanged() {
      this.$emit('modifierChanged', this.modifier, this.field);
    },
    enterPressed() {
      if (this.inputSelection) {
        this.$emit('selected', this.inputSelection, this.field);
        this.inputSelection = '';
      }
    },
  },
};
</script>
<style lang="scss">
  .dropdown, .dropdown-trigger, input[type='text'] {
    width: 100%;
  }
</style>
