<script>
import { mapActions, mapGetters } from 'vuex';

import Airflow from '@/components/orchestration/Airflow'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Orchestration',
  components: {
    Airflow,
    RouterViewLayout
  },
  created() {
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
      'getIsInstallingPlugin'
    ]),
    getIsInstallingAirflow() {
      return this.getIsInstallingPlugin('orchestrators', 'airflow');
    },
  },
  methods: {
  ...mapActions('plugins', [
    'addPlugin',
    'installPlugin',
  ]),
  installAirflow() {
    const payload = { pluginType: 'orchestrators', name: 'airflow' };
    this.addPlugin(payload)
      .then(() => {
        this.installPlugin(payload);
      });
    },
  },
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
              <p>Airflow is Meltano's current orchestrator. Learn what's possible in the <a target='_blank' href="https://www.meltano.com/docs/meltano-cli.html#orchestration">Meltano Airflow</a> documentation.</p>
              <p v-if='getIsInstallingAirflow' class="is-italic">Airflow installation can take a few minutes.</p>
              <a
                class="button is-interactive-primary"
                :class='{ "is-loading": getIsInstallingAirflow }'
                @click='installAirflow'>
                Install Airflow
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </router-view-layout>
</template>

<style lang="scss" scoped></style>
