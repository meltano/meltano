<script>
import { mapGetters, mapState } from 'vuex'

import CreatePipelineSchedule from '@/components/pipelines/CreatePipelineSchedule'
import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Datasets',
  components: {
    CreatePipelineSchedule,
    PipelineSchedules,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('orchestration', ['getHasPipelines']),
    ...mapGetters('plugins', [
      'getIsStepLoadersMinimallyValidated',
      'getIsStepScheduleMinimallyValidated'
    ]),
    ...mapState('plugins', ['installedPlugins']),
    ...mapState('orchestration', ['installedPlugins']),
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
  },
  created() {
    this.$store.dispatch('orchestration/getAllPipelineSchedules')
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <h2 class="title">Datasets</h2>
      <p class="subtitle">Integrations and custom data connections</p>

      <div class="columns">
        <div class="column">
          <CreatePipelineSchedule />
        </div>
      </div>

      <div v-if="getHasPipelines" class="columns">
        <div class="column">
          <div class="content">
            <h3 class="title">Pipelines</h3>
            <p class="subtitle">Scheduled dataset collection</p>
          </div>
          <PipelineSchedules />
        </div>
      </div>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
