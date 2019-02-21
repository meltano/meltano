<template>
  <div class="control">
    <div class="tags has-addons">
        <span class="tag">{{name}}</span>
        <a class="tag is-delete" @click.prevent="$emit('delete')"></a>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Pill',
  props: ['user', 'name'],
};
</script>
