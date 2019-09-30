<script>
import Vue from 'vue'
import { mapActions, mapGetters } from 'vuex'

import Toasted from 'vue-toasted'

import Breadcrumbs from '@/components/navigation/Breadcrumbs'
import MainNav from '@/components/navigation/MainNav'

export default {
  name: 'App',
  components: {
    Breadcrumbs,
    MainNav
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsAddingPlugin',
      'getIsInstallingPlugin',
      'getIsPluginInstalled'
    ])
  },
  created() {
    this.autoInstallAirflowCheck()
    this.acknowledgeAnalyticsTracking()
  },
  methods: {
    ...mapActions('plugins', ['addPlugin', 'installPlugin']),
    acknowledgeAnalyticsTracking() {
      if (Vue.prototype.$flask.isSendAnonymousUsageStats) {
        const hasAcknowledgedTracking =
          'hasAcknowledgedTracking' in localStorage &&
          localStorage.getItem('hasAcknowledgedTracking') === 'true'
        if (!hasAcknowledgedTracking) {
          Vue.toasted.global.acknowledgeAnalyticsTracking()
        }
      }
    },
    autoInstallAirflowCheck() {
      this.$store.dispatch('plugins/getInstalledPlugins').then(() => {
        const needsInstallation =
          !this.getIsAddingPlugin('orchestrators', 'airflow') &&
          !this.getIsInstallingPlugin('orchestrators', 'airflow') &&
          !this.getIsPluginInstalled('orchestrators', 'airflow')
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
