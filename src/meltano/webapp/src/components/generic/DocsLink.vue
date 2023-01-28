<script>
import utils from '@/utils/utils'

export default {
  name: 'DocsLink',
  props: {
    fragment: {
      type: String,
      default: '',
    },
    page: {
      type: String,
      default: '',
    },
    target: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      linkPage: `/${this.page}`,
      linkTarget: this.target || '_blank',
    }
  },

  computed: {
    url() {
      return utils.docsUrl(this.linkPage, this.fragment)
    },
  },
}
</script>

<template>
  <a :href="url" :target="linkTarget">
    <slot />
  </a>
</template>

<style lang="scss"></style>
