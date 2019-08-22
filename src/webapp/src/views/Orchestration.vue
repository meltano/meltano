<script>
import { mapGetters } from 'vuex'

import Airflow from '@/components/orchestration/Airflow'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Orchestration',
  components: {
    Airflow,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('plugins', ['getIsPluginInstalled', 'getIsInstallingPlugin']),
    getIsInstallingAirflow() {
      return this.getIsInstallingPlugin('orchestrators', 'airflow')
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class="is-marginless">Orchestration</h1>
        </div>
      </div>
    </div>

    <div class="container view-body">
      <airflow
        v-if="getIsPluginInstalled('orchestrators', 'airflow')"
      ></airflow>
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
