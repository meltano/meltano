<template>
  <div class="columns is-gapless">
    <section class="column is-full vh-scrollable">
      <div class='box-transparent box is-radiusless is-shadowless'>
        <slot name="default"></slot>
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
</style>
