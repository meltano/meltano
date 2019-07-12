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
    disabled: {
      type: Boolean,
      default: false,
    },
    isCaretRemoved: {
      type: Boolean,
      default: false,
    },
    isFullWidth: {
      type: Boolean,
    },
    isRightAligned: {
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
        }">
    <div class="dropdown-trigger">
      <button class="button"
              :class="buttonClasses"
              :disabled="disabled"
              :aria-controls="getHyphenatedLabel"
              aria-haspopup="true"
              @click="toggleDropdown">
        <span v-if="label">{{label}}</span>
        <span v-if='!isCaretRemoved' class="icon is-small">
          <font-awesome-icon :icon="isOpen ? 'caret-up' : 'caret-down'"></font-awesome-icon>
        </span>
      </button>
    </div>
    <div class="dropdown-menu"
         :class="menuClasses"
         :id="getHyphenatedLabel"
         role="menu">
      <slot :dropdown-close="close"></slot>
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
