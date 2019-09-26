<script>
import Breadcrumbs from '@/components/navigation/Breadcrumbs'
import MainNav from '@/components/navigation/MainNav'

export default {
  name: 'App',
  components: {
    Breadcrumbs,
    MainNav
  },
  created() {
    // TODO: poller?
    this.$store.dispatch('system/check')
  }
}
</script>

<template>
  <div id="app">
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
