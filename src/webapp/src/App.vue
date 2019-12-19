<script>
import Breadcrumbs from '@/components/navigation/Breadcrumbs'
import MainNav from '@/components/navigation/MainNav'
import PromoBanner from '@/components/generic/PromoBanner'

export default {
  name: 'App',
  components: {
    Breadcrumbs,
    MainNav,
    PromoBanner
  },
  computed: {
    isMeltanoDemoSite() {
      return window.location.host === 'meltano.meltanodata.com'
    }
  },
  created() {
    this.$store.dispatch('system/check')
    this.$store.dispatch('system/fetchIdentity')
    this.tryAcknowledgeAnalyticsTracking()
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
    <Breadcrumbs></Breadcrumbs>
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
