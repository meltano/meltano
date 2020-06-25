<script>
import { mapActions, mapGetters } from 'vuex'

import PipelineSchedules from '@/components/pipelines/PipelineSchedules'
import CreatePipelineScheduleModal from '@/components/pipelines/CreatePipelineScheduleModal.vue'

import RouterViewLayout from '@/views/RouterViewLayout'

export default {
  name: 'Pipelines',
  components: {
    PipelineSchedules,
    RouterViewLayout,
    CreatePipelineScheduleModal
  },
  data() {
    return {
      isLoading: false,
      isCreatePipelineModalOpen: false
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
    ...mapActions('orchestration', ['getPipelineSchedules']),
    toggleCreatePipelineModal() {
      this.isCreatePipelineModalOpen = !this.isCreatePipelineModalOpen
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-widescreen">
      <div class="columns">
        <div class="column">
          <h2 id="data" class="title">Pipelines</h2>
        </div>
        <div class="column is-one-quarter has-text-right">
          <button
            class="button is-interactive-primary"
            @click.stop="toggleCreatePipelineModal"
          >
            Create
          </button>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div v-if="getHasPipelines">
            <PipelineSchedules :pipelines="getSortedPipelines" />
          </div>
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
    <create-pipeline-schedule-modal 
      v-if="isCreatePipelineModalOpen" 
      @close="toggleCreatePipelineModal"
    />
  </router-view-layout>
</template>

<style lang="scss"></style>
