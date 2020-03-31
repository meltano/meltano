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
  data() {
    return {
      isLoading: false
    }
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
    this.isLoading = true
    this.getPipelineSchedules().then(() => (this.isLoading = false))
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

      <div class="columns">
        <div class="column">
          <PipelineSchedules
            v-if="getHasPipelines"
            :pipelines="getSortedPipelines"
          />
          <div v-else class="box">
            <progress
              v-if="isLoading"
              class="progress is-small is-info"
            ></progress>
            <div v-else>
              <div class="content">
                <p>
                  No pipelines have been set up yet.
                  <router-link to="connections"
                    >Connect a data source</router-link
                  >
                  first.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isModal">
        <router-view :name="getModalName"></router-view>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss"></style>
