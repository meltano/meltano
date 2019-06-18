<script>

export default {
  name: 'RouterViewLayoutSidebar',
};

</script>

<template>
  <div class="columns is-gapless">
    <aside class="column is-one-quarter vh-scrollable">
      <div class='box-transparent box is-radiusless is-shadowless'>
        <slot name="left"></slot>
      </div>
    </aside>
    <section class="column is-three-quarters vh-scrollable">
      <div class='box-transparent box is-radiusless is-shadowless'>
        <slot name="right"></slot>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped>
</style>
