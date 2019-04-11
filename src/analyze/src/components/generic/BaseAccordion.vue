<script>
export default {
  name: 'BaseAccordion',
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isToggleOpen: this.isOpen,
    };
  },
  methods: {
    toggleIsOpen() {
      this.isToggleOpen = !this.isToggleOpen;
    },
  },
};
</script>

<template>
  <section class="accordion">
    <div class="accordion-header" @click="toggleIsOpen">
      <slot name="header"></slot>
    </div>
    <div class="accordion-body" :class="{ 'is-open': isToggleOpen }">
      <div class="accordion-content">
        <slot name="body"></slot>
      </div>
    </div>
  </section>
</template>

<style lang="scss">
.accordion {
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 2rem;
}

.accordion-header {
  align-items: center;
  background-color: #0F3B66;
  border-radius: 4px 4px 0 0;
  color: #dbdbdb;
  display: flex;
  justify-content: space-between;
  line-height: 1.25;
  padding: 1rem 1.5rem;
  position: relative;
}

.accordion-body {
  overflow-y: hidden;
  max-height: 0;
  color: #4a4a4a;
  border: 1px solid #dbdbdb;
  border-radius: 4px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  border-top: none;
  transition: max-height .2s ease;

  &.is-open {
    max-height: 10000rem;
  }
}

.accordion-content {
  padding: 1em 1.25em;
}
</style>
