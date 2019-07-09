<script>
export default {
  name: 'Pill',
  props: ['user', 'name'],
};
</script>

<template>
  <p class="control">
    <div class="tags has-addons">
        <span class="tag">{{name}}</span>
        <a class="tag is-delete" @click.prevent="$emit('delete')"></a>
    </div>
  </p>
</template>

<style lang="scss">
</style>
