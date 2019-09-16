<script>
import { mapGetters } from 'vuex'

import Airflow from '@/components/orchestration/Airflow'
import RouterViewLayout from '@/views/RouterViewLayout'
import flaskContext from '@/flask'


export default {
  name: 'Orchestration',
  components: {
    Airflow,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('plugins', ['getIsInstallingPlugin', 'getIsPluginInstalled']),
    getIsAirflowReady() {
      return !this.getIsInstallingAirflow && this.getIsAirflowInstalled
    },
    getIsAirflowInstalled() {
      return this.getIsPluginInstalled('orchestrators', 'airflow')
    },
    getIsInstallingAirflow() {
      return this.getIsInstallingPlugin('orchestrators', 'airflow')
    }
  },
  beforeRouteEnter: (to, from, next) => {
    // force refresh unless the Flask context has Airflow set
    const { airflowUrl } = flaskContext()

    if (!airflowUrl && from.name !== null) {
      window.location.href = to.path
    } else {
      next()
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <airflow v-if="getIsAirflowReady"></airflow>
      <section v-else>
        <div class="columns">
          <div class="column">
            <div class="content">
              <template v-if="getIsInstallingAirflow">
                <p>
                  Airflow is Meltano's current orchestrator. Learn what's
                  possible in the
                  <a
                    target="_blank"
                    href="https://www.meltano.com/docs/meltano-cli.html#orchestration"
                    >Meltano Airflow</a
                  >
                  documentation.
                </p>
                <hr />
                <p class="is-italic has-text-centered">
                  Airflow installation can take a few minutes.
                </p>
              </template>

              <p>
                <progress class="progress is-small is-info"></progress>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss" scoped></style>
