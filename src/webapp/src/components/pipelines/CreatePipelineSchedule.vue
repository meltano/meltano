<script>
import { mapGetters, mapState } from 'vuex'
import Vue from 'vue'

export default {
  name: 'CreatePipelineSchedule',
  data() {
    return {
      intervalOptions: [
        '@once',
        '@hourly',
        '@daily',
        '@weekly',
        '@monthly',
        '@yearly'
      ],
      isSaving: false,
      pipeline: {
        name: '',
        extractor: '',
        loader: '',
        transform: '',
        interval: '',
        isRunning: false
      }
    }
  }
}
</script>

<template>
  <div>
    Inline Create Pipeline Placeholder
  </div>
</template>

<style lang="scss"></style>
