<script>
export default {

};
</script>

<template>
  <section class="card">
    <slot></slot>
  </section>
</template>

<style lang="scss" scoped>
.card {
  border-radius: 2px;
  position: relative;
  box-sizing: border-box;
  box-shadow: none;
  font-size: 12px;
  line-height: 1.3;
  transition: box-shadow .4s cubic-bezier(.25, .8, .25, 1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  &:hover {
    box-shadow: 0px 8px 24px 0px rgba(0, 0, 0, .24);
  }
}
</style>
