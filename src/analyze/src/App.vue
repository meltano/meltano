<template>
  <div id="app">
    <main-nav></main-nav>
    <router-view/>
  </div>
</template>

<script>
import MainNav from './components/MainNav';

export default {
  name: 'App',
  components: {
    MainNav,
  },
};
</script>
<style lang="scss">
@import "scss/main.scss";
</style>
