<script>
export default {
  name: 'RouterViewLayout',
}
</script>

<template>
  <div class="columns is-gapless">
    <section class="column is-full">
      <div class="box-transparent box is-radiusless is-shadowless">
        <slot name="default"></slot>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped></style>
