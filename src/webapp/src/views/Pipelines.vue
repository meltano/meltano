<script>
import { mapState } from 'vuex'

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
          routeMatches: ['extractors', 'extractorSettings', 'extractorEntities']
        },
        {
          name: 'loaders',
          routeMatches: ['loaders', 'loaderSettings']
        },
        {
          name: 'transforms',
          routeMatches: ['transforms']
        },
        {
          name: 'schedules',
          routeMatches: ['schedules', 'createSchedule']
        }
      ]
    }
  },
  computed: {
    ...mapState('plugins', ['installedPlugins']),
    currentStep() {
      return this.steps.find(step =>
        step.routeMatches.find(match => this.$route.name === match)
      )
    },
    getIsActiveStep() {
      return stepName => this.currentStep.name === stepName
    },
    getIsStepExtractorsMinimallyValidated() {
      return (
        this.installedPlugins.extractors &&
        this.installedPlugins.extractors.length > 0
      )
    },
    getIsStepLoadersMinimallyValidated() {
      return this.getIsStepExtractorsMinimallyValidated
    },
    getIsStepTransformsMinimallyValidated() {
      return this.getIsStepLoadersMinimallyValidated
    },
    getIsStepScheduleMinimallyValidated() {
      return (
        this.getIsStepTransformsMinimallyValidated &&
        this.installedPlugins.loaders &&
        this.installedPlugins.loaders.length > 0
      )
    },
    getModalName() {
      return this.$route.name
    },
    isModal() {
      return this.$route.meta.isModal
    }
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
    <div class="container view-header">
      <div class="content">
        <div class="level">
          <h1 class="is-marginless">Pipelines</h1>
        </div>
      </div>
    </div>

    <div class="container view-body">
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
            <p>Connect to Data</p>
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
            <p>Store Selected Data</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('transforms'),
            'is-completed': getIsStepTransformsMinimallyValidated
          }"
        >
          <div class="step-marker">3</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation"
              :class="{ 'is-active': getIsActiveStep('transforms') }"
              :disabled="!getIsStepTransformsMinimallyValidated"
              @click="setStep('transforms')"
            >
              Transform
            </button>
            <p>Transform Loaded Data</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('schedule'),
            'is-completed': getIsStepScheduleMinimallyValidated
          }"
        >
          <div class="step-marker">4</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation is-outlined"
              :class="{ 'is-active': getIsActiveStep('schedules') }"
              :disabled="!getIsStepScheduleMinimallyValidated"
              @click="setStep('schedules')"
            >
              Run
            </button>
            <p>Automate Data Collection</p>
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
