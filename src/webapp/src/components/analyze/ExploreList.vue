<script>
import { mapGetters } from 'vuex'

export default {
  name: 'ExploreList',
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'installedExtractors'])
  },
  methods: {
    goToExplore(extractor) {
      this.$router.push({
        name: 'explore',
        params: { extractor }
      })
    }
  }
}
</script>

<template>
  <div>
    <a
      v-for="extractor in installedExtractors"
      :key="extractor.name"
      class="navbar-item"
      @click="goToExplore(extractor.name)"
    >
      {{ extractor.label || extractor.name }}
    </a>
  </div>
</template>

<style lang="scss"></style>
