<template>
  <div class="columns is-gapless">
    <aside class="column is-one-quarter vh-scrollable has-background-white-bis">
      <div class='box is-radiusless is-shadowless'>
        <slot name="left"></slot>
      </div>
    </aside>
    <section class="column is-three-quarters vh-scrollable">
      <div class='box is-radiusless is-shadowless'>
        <slot name="right"></slot>
      </div>
    </section>
  </div>
</template>

<script>

export default {
  name: 'RouterViewLayout',
};

</script>

<style lang="scss" scoped>

.vh-scrollable {
  height: calc(100vh - 3.25rem); // TODO properly import variable $navbar-height when on Vue CLI3
  overflow-y: scroll;
  overflow-x: hidden;
}

</style>
