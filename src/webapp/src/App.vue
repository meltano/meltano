<script>
import { mapActions, mapGetters } from 'vuex'

import MainNav from './components/generic/MainNav'

export default {
  name: 'App',
  components: {
    MainNav
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin'])
  },
  created() {
    this.autoInstallAirflowCheck()
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    autoInstallAirflowCheck() {
      this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
        const needsInstallation =
          !this.getIsPluginInstalled('orchestrators', 'airflow') &&
          !this.getIsInstallingPlugin('orchestrators', 'airflow')
        if (needsInstallation) {
          const payload = { pluginType: 'orchestrators', name: 'airflow' }
          this.addPlugin(payload).then(() => {
            this.installPlugin(payload)
          })
        }
      })
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
