<script>
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Analyze',
  components: {
    RouterViewLayout
  },
  computed: {
    isModal() {
      return this.$route.meta && this.$route.meta.isModal
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <router-view />
      <div v-if="isModal">
        <router-view :name="$route.name"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
