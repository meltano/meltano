<template>
  <ParentPage :sidebarItems="sidebarItems">
    <template #top>
      <slot name="top" />

      <PageOutdated />
    </template>

    <template #bottom>
      <slot name="bottom" />

      <GlobalFooter />
    </template>
  </ParentPage>
</template>

<script>
import ParentPage from '@parent-theme/components/Page.vue'
import PageOutdated from '@theme/components/PageOutdated.vue'

export default {
  components: { ParentPage, PageOutdated },
  props: ['sidebarItems']
}
</script>

<style lang="stylus">
.page
  padding-bottom 0
</style>
