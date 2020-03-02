<script>
import { mapActions, mapGetters } from 'vuex'

import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Pipelines',
  components: {
    PipelineSchedules,
    RouterViewLayout
  },
  computed: {
    ...mapGetters('orchestration', ['getHasPipelines', 'getSortedPipelines']),
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
  },
  created() {
    this.getPipelineSchedules()
  },
  methods: {
    ...mapActions('orchestration', ['getPipelineSchedules'])
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <h2 id="data" class="title">Pipelines</h2>
      <p class="subtitle">Scheduled data collection</p>

      <template v-if="getHasPipelines" class="columns">
        <div class="columns">
          <div class="column">
            <PipelineSchedules :pipelines="getSortedPipelines" />
          </div>
        </div>
      </template>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
