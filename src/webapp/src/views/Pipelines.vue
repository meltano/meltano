<script>
import { mapGetters, mapState } from 'vuex'

import RouterViewLayout from '@/views/RouterViewLayout'
import Step from '@/components/generic/bulma/Step'

export default {
  name: 'Pipelines',
  components: {
    RouterViewLayout,
    Step
  },
  data() {
    return {
      steps: [
        {
          name: 'extractors',
          routeMatches: ['extractors', 'extractorSettings']
        },
        {
          name: 'loaders',
          routeMatches: ['loaders', 'loaderSettings']
        },
        {
          name: 'schedules',
          routeMatches: ['schedules', 'createPipelineSchedule', 'runLog']
        }
      ]
    }
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsStepLoadersMinimallyValidated',
      'getIsStepScheduleMinimallyValidated'
    ]),
    ...mapState('plugins', ['installedPlugins']),
    ...mapState('orchestration', ['installedPlugins']),
    currentStep() {
      return this.steps.find(step =>
        step.routeMatches.find(match => this.$route.name === match)
      )
    },
    getIsActiveStep() {
      return stepName => this.currentStep.name === stepName
    },
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins')
    this.$store.dispatch('plugins/getInstalledPlugins')
  },
  methods: {
    setStep(stepName) {
      const targetStep = this.steps.find(step => step.name === stepName)
      this.$router.push(targetStep)
    }
  }
}
</script>

<template>
  <router-view-layout>
    <div class="container view-body is-fluid">
      <div id="steps-data-setup" class="steps steps-pipelines is-small">
        <div
          class="step-item is-completed"
          :class="{ 'is-active': getIsActiveStep('extractors') }"
        >
          <div class="step-marker">1</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation"
              :class="{ 'is-active': getIsActiveStep('extractors') }"
              @click="setStep('extractors')"
            >
              Extract
            </button>
            <p>Pull Raw Data from Source</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('loaders'),
            'is-completed': getIsStepLoadersMinimallyValidated
          }"
        >
          <div class="step-marker">2</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation"
              :class="{ 'is-active': getIsActiveStep('loaders') }"
              :disabled="!getIsStepLoadersMinimallyValidated"
              @click="setStep('loaders')"
            >
              Load
            </button>
            <p>Push Raw Data to Destination</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('schedule'),
            'is-completed': getIsStepScheduleMinimallyValidated
          }"
        >
          <div class="step-marker">3</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation is-outlined"
              :class="{ 'is-active': getIsActiveStep('schedules') }"
              :disabled="!getIsStepScheduleMinimallyValidated"
              @click="setStep('schedules')"
            >
              Schedule
            </button>
            <p>Automate Extract & Load</p>
          </div>
        </div>

        <div class="steps-content">
          <Step>
            <router-view></router-view>
            <div v-if="isModal">
              <router-view :name="getModalName"></router-view>
            </div>
          </Step>
        </div>
      </div>
    </div>
  </router-view-layout>
</template>

<style lang="scss">
.steps-pipelines {
  margin-top: 2rem;
}
</style>
