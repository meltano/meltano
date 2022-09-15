<script>
import MainNav from '@/components/navigation/MainNav'

export default {
  name: 'App',
  components: {
    MainNav
  },
  computed: {
    isMeltanoDataInstance() {
      const url = new URL(window.location.host)
      return url.hostname.endsWith('meltanodata.com')
    }
  },
  created() {
    const isUpdateCheckEnabled = this.$flask.isUpdateCheckEnabled
    this.$store.dispatch('system/check', {
      include_latest: isUpdateCheckEnabled
    })

    this.$store.dispatch('system/fetchIdentity')
    this.tryAcknowledgeAnalyticsTracking()
  },
  mounted() {
    if (this.isMeltanoDataInstance) {
      this.$intercom.boot()
    }
  },
  methods: {
    tryAcknowledgeAnalyticsTracking() {
      if (this.$flask.isSendAnonymousUsageStats) {
        const hasAcknowledgedTracking =
          'hasAcknowledgedTracking' in localStorage &&
          localStorage.getItem('hasAcknowledgedTracking') === 'true'
        if (!hasAcknowledgedTracking) {
          this.$toasted.global.acknowledgeAnalyticsTracking()
        }
      }
    }
  }
}
</script>

<template>
  <div id="app">
    <main-nav></main-nav>
    <router-view />
  </div>
</template>

<style lang="scss">
@import 'scss/_index.scss';

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
