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
      const url = utils.docsUrl(this.linkPage, this.fragment);

      return url;
    },
  },
};
</script>

<template>
  <a :href="url" :target="linkTarget">
    <slot/>
  </a>
</template>
