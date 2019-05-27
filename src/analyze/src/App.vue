<template>
  <div id="app">
    <main-nav></main-nav>
    <router-view/>
  </div>
</template>

<script>
import MainNav from './components/generic/MainNav';

export default {
  name: 'App',
  components: {
    MainNav,
  },
};
</script>
<style lang="scss">
 @import "scss/_index.scss";

 #app {
   min-height: 100vh;
   display: flex;
   flex-direction: column;
 }
</style>
