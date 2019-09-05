<script>
export default {
  name: 'Breadcrumbs',
  computed: {
    crumbs() {
      let path = this.$route.path.substr(1, this.$route.path.length)
      if (path.charAt(path.length - 1) === '/') {
        path = path.substr(0, path.length - 1)
      }
      return path.split('/')
    }
  }
}
</script>

<template>
  <nav class="breadcrumb is-small" aria-label="breadcrumbs">
    <ul>
      <!-- li.is-active is temporary until we make breadcrumbs interactive (requires improved route parsing approach) -->
      <li v-for="crumb in crumbs" :key="crumb" class="is-active">
        <a class="is-capitalized">{{ crumb }}</a>
      </li>
    </ul>
  </nav>
</template>

<style lang="scss"></style>
