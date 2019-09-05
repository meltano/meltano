<script>
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Analyze',
  components: {
    RouterViewLayout
  },
  computed: {
    isCurrentPath() {
      return path => this.$route.path.includes(path)
    },
    isModal() {
      return this.$route.meta && this.$route.meta.isModal
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-header">
      <div class="content">
        <div class="level">
          <div class="level-left">
            <h1 class="is-marginless">Analyze</h1>
          </div>
          <div class="level-right">
            <div class="tabs is-right">
              <ul>
                <li :class="{ 'is-active': isCurrentPath('/analyze/models') }">
                  <router-link :to="{ name: 'analyzeModels' }"
                    >Models</router-link
                  >
                </li>
                <li
                  class="is-marginless"
                  :class="{ 'is-active': isCurrentPath('/analyze/settings') }"
                >
                  <router-link :to="{ name: 'analyzeSettings' }"
                    >Connections</router-link
                  >
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container view-body is-fluid">
      <router-view />
      <div v-if="isModal">
        <router-view :name="$route.name"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
