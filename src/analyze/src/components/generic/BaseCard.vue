<script>
export default {

}
</script>

<template>
	<section class="card">
    <slot></slot>
  </section>
</template>

<style lang="scss" scoped>
.card {
  border-radius: 2px;
  width: 328px;
  height: 152px;
  margin: 12px;
  position: relative;
  box-shadow: none;
  font-size: 12px;
  line-height: 1.3;
  transition: box-shadow .4s cubic-bezier(.25, .8, .25, 1);

  &:hover {
    box-shadow: 0px 8px 24px 0px rgba(0, 0, 0, .24);
  }
}
</style>
