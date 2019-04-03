<script>
export default {
  props: {
    isOpen: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<template>
  <section class="accordion">
    <div class="accordion-header" @click="isOpen = !isOpen">
      <slot name="header"></slot>
    </div>
    <div class="accordion-body" :class="{ 'is-open': isOpen }">
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
  background-color: #4a4a4a;
  border-radius: 4px 4px 0 0;
  color: #dbdbdb;
  display: flex;
  justify-content: space-between;
  line-height: 1.25;
  padding: .5em .75em;
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
    max-height: 100rem;
  }
}

.accordion-content {
  padding: 1em 1.25em;
}
</style>

