<template>
  <ParentLayout />
</template>

<script>
import ParentLayout from '@parent-theme/layouts/Layout.vue'

export default {
  name: 'Layout',
  components: {
    ParentLayout,
  },
  data() {
    return {
      isEmbedded: false,
    }
  },
  created() {
    this.isEmbedded = this.$route.query["embed"] === 'true'

    if (this.isEmbedded) {
      this.$page.frontmatter.navbar = false
      this.$page.frontmatter.sidebar = false
    }
  },
  mounted() {
    // Intercom.io chat
    if (!this.isEmbedded) {
      this.$intercom.boot()
    }
  }
}
</script>

<style lang="stylus">
@require '../styles/vuepress-theme-default-prefers-color-scheme/components.styl'
</style>
