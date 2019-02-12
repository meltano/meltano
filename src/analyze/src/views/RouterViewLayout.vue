<template>
  <div class="columns is-gapless">
    <aside class="column is-one-quarter has-background-white-bis menu">
      <slot name="left"></slot>
    </aside>
    <section class="column is-three-quarters">
      <slot name="right"></slot>
    </section>
  </div>
</template>

<script>

export default {
  name: 'RouterViewLayout',
};

</script>

<style lang="scss" scoped>
</style>
