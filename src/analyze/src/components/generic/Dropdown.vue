<script>
import hyphenate from '@/filters/hyphenate';

export default {
  name: 'Dropdown',
  created() {
    document.addEventListener('click', this.onDocumentClick);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.onDocumentClick);
  },
  data() {
    return {
      isOpen: false,
      lastDropdownOpen: null,
    };
  },
  computed: {
    getHyphenatedLabel() {
      return hyphenate(this.label, 'dropdown');
    },
  },
  filters: {
    hyphenate,
  },
  props: {
    label: {
      type: String,
    },
    buttonClasses: {
      type: String,
    },
    menuClasses: {
      type: String,
    },
    iconOpen: {
      type: String,
      default: 'caret-down',
    },
    iconClose: {
      type: String,
      default: 'caret-up',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    isIconRemoved: {
      type: Boolean,
      default: false,
    },
    isFullWidth: {
      type: Boolean,
    },
    isRightAligned: {
      type: Boolean,
    },
    isUp: {
      type: Boolean,
    },
  },
  methods: {
    close() {
      this.isOpen = false;
    },
    open() {
      this.isOpen = true;
    },
    toggleDropdown() {
      this.isOpen = !this.isOpen;
    },
    onBubbleClose(e) {
      if ('dropdownAutoClose' in e.target.dataset) {
        this.close();
      }
    },
    onDocumentClick(el) {
      const targetEl = el.target.closest('.dropdown');
      const matchEl = this.$el.closest('.dropdown');
      if (targetEl !== matchEl) {
        this.close();
      }
    },
  },
};
</script>

<template>
  <div class="dropdown"
        :class="{
          'is-active': isOpen,
          'is-right': isRightAligned,
          'is-fullwidth': isFullWidth,
          'is-up': isUp,
        }"
        @click='onBubbleClose'>
    <div class="dropdown-trigger">
      <button class="button"
              :class="buttonClasses"
              :disabled="disabled"
              :aria-controls="getHyphenatedLabel"
              aria-haspopup="true"
              @click="toggleDropdown">
        <span v-if="label">{{label}}</span>
        <span v-if='!isIconRemoved' class="icon is-small">
          <font-awesome-icon :icon="isOpen ? iconClose : iconOpen"></font-awesome-icon>
        </span>
      </button>
    </div>
    <div class="dropdown-menu"
         :class="menuClasses"
         :id="getHyphenatedLabel"
         role="menu">
      <slot></slot>
    </div>
  </div>
</template>

<style lang="scss">
.dropdown.is-fullwidth {
  width: 100%;

  .dropdown-trigger {
    width: 100%
  }

  .button {
    display: flex;
    width: 100%;
    justify-content: space-between
  }
}
.dropdown-menu {
  // TODO refactor into a better approach for target widths while accounting for the app breakpoints
  // Ideally we can inject the SCSS vars, mixins, etc and leverage them in components to leverage a style SSOT
  &.dropdown-menu-600 {
    width: 600px;
  }
}
</style>
