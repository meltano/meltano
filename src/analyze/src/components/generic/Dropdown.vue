<template>
  <div class="dropdown"
        :class="{'is-active': isOpen}">
    <div class="dropdown-trigger">
      <button class="button"
              aria-haspopup="true"
              :aria-controls="getHyphenatedLabel"
              @click="toggleDropdown">
        <span>{{label}}</span>
        <span class="icon is-small">
          <font-awesome-icon icon="caret-down" style="color:black;"></font-awesome-icon>
        </span>
      </button>
    </div>
    <div class="dropdown-menu" :id="getHyphenatedLabel" role="menu">
      <slot :dropdown-force-close="forceClose"></slot>
    </div>
  </div>
</template>

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
  },
  methods: {
    forceClose() {
      this.isOpen = false;
    },
    toggleDropdown() {
      this.isOpen = !this.isOpen;
    },
    onDocumentClick(el) {
      const targetEl = el.target.closest('.dropdown');
      const matchEl = this.$el.closest('.dropdown');
      if (targetEl !== matchEl) {
        this.forceClose();
      }
    },
  },
};
</script>

<style lang="scss">

</style>
