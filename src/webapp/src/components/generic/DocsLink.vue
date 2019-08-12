<script>
import utils from '@/utils/utils';

export default {
  name: 'DocsLink',
  props: ['page', 'fragment', 'target'],

  data() {
    return {
      linkPage: `/${this.page}`,
      linkTarget: this.target || '_blank',
    };
  },

  computed: {
    url() {
      return utils.docsUrl(this.linkPage, this.fragment);
    },
  },
};
</script>

<template>
  <a :href="url" :target="linkTarget">
    <slot/>
  </a>
</template>

<style lang="scss">
</style>
