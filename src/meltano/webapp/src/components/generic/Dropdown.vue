<script>
import hyphenate from '@/filters/hyphenate'

export default {
  name: 'Dropdown',
  filters: {
    hyphenate,
  },
  props: {
    buttonClasses: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    iconClose: {
      type: String,
      default: 'caret-up',
    },
    iconOpen: {
      type: String,
      default: 'caret-down',
    },
    isIconRemoved: {
      type: Boolean,
      default: false,
    },
    isFullWidth: {
      type: Boolean,
      default: false,
    },
    isRightAligned: {
      type: Boolean,
      default: false,
    },
    isUp: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: '',
    },
    labelClasses: {
      type: String,
      default: '',
    },
    menuClasses: {
      type: String,
      default: '',
    },
    textIs: {
      type: String,
      default: '',
    },
    tooltip: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  data() {
    return {
      isOpen: false,
      lastDropdownOpen: null,
    }
  },
  computed: {
    getButtonClasses() {
      return () => {
        let classes = this.buttonClasses
        if (this.tooltip.message) {
          classes += ` tooltip ${this.tooltip.classes}`
        }
        return classes
      }
    },
    getHyphenatedLabel() {
      return hyphenate(this.label, 'dropdown')
    },
  },
  created() {
    document.addEventListener('click', this.onDocumentClick)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.onDocumentClick)
  },
  methods: {
    close() {
      this.isOpen = false
      this.$emit('dropdown:close')
    },
    open(payload) {
      this.isOpen = true
      this.$emit('dropdown:open', payload)
    },
    toggleDropdown() {
      this.isOpen ? this.close() : this.open()
    },
    onBubbleClose(e) {
      if ('dropdownAutoClose' in e.target.dataset) {
        this.close()
      }
    },
    onDocumentClick(el) {
      const targetEl = el.target.closest('.dropdown')
      const matchEl = this.$el.closest('.dropdown')
      if (targetEl !== matchEl) {
        this.close()
      }
    },
  },
}
</script>

<template>
  <div
    class="dropdown"
    :class="{
      'is-active': isOpen,
      'is-right': isRightAligned,
      'is-fullwidth': isFullWidth,
      'is-up': isUp,
    }"
    @click.stop="onBubbleClose"
  >
    <div class="dropdown-trigger">
      <button
        class="button"
        :class="getButtonClasses()"
        :disabled="disabled"
        :aria-controls="getHyphenatedLabel"
        aria-haspopup="true"
        :data-tooltip="tooltip.message"
        @click="toggleDropdown"
      >
        <span class="text-is">{{ textIs }}</span>
        <span v-if="label" :class="labelClasses">{{ label }}</span>
        <span v-if="!isIconRemoved" class="icon is-small">
          <font-awesome-icon
            :icon="isOpen ? iconClose : iconOpen"
          ></font-awesome-icon>
        </span>
      </button>
    </div>
    <div
      :id="getHyphenatedLabel"
      class="dropdown-menu"
      :class="menuClasses"
      role="menu"
    >
      <slot></slot>
    </div>
  </div>
</template>

<style lang="scss">
.dropdown.is-fullwidth {
  width: 100%;

  .dropdown-trigger {
    width: 100%;
  }

  .button {
    display: flex;
    width: 100%;
    justify-content: space-between;
  }
}
.dropdown-menu {
  // TODO refactor into a better approach for target widths while accounting for the app breakpoints
  // Ideally we can inject the SCSS vars, mixins, etc and leverage them in components to leverage a style SSOT
  &.dropdown-menu-600 {
    width: 600px;
  }
  &.dropdown-menu-300 {
    width: 300px;
  }
}
</style>
