<script>
import MainNav from '@/components/navigation/MainNav'
import PromoBanner from '@/components/generic/PromoBanner'

export default {
  name: 'App',
  components: {
    MainNav,
    PromoBanner
  },
  computed: {
    isMeltanoDataInstance() {
      return window.location.host.indexOf('meltanodata.com') > -1
    },
    isMeltanoDemoSite() {
      return window.location.host === 'meltano.meltanodata.com'
    }
  },
  created() {
    this.$store.dispatch('system/check')
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
    <PromoBanner v-if="isMeltanoDemoSite"></PromoBanner>
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
