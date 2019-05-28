<template>
  <a :href="url" :target="linkTarget">
    <slot/>
  </a>
</template>

<script>
import utils from '@/utils/utils';

export default {
  name: 'DocsLink',
  props: ['page', 'fragment', 'target'],

  data: function() {
    return {
      linkPage: `/${this.page}`,
      linkTarget: this.target || "_blank",
    };
  },

  computed: {
    url: function() {
      const url = utils.docsUrl(this.linkPage, this.fragment);
      console.log(url);

      return url;
    },
  },
};
</script>
