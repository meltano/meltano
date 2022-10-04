<script>
import MainNav from '@/components/navigation/MainNav'

export default {
  name: 'App',
  components: {
    MainNav,
  },
  computed: {
    isMeltanoDataInstance() {
      const url = new URL(window.location.host)
      return url.hostname.endsWith('meltanodata.com')
    },
  },
  created() {
    this.$store.dispatch('system/check')
    this.$store.dispatch('system/fetchIdentity')
  },
  mounted() {
    if (this.isMeltanoDataInstance) {
      this.$intercom.boot()
    }
  },
  methods: {},
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
