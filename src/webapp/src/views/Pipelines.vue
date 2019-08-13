<script>
import { mapState } from 'vuex'

import ClosableMessage from '@/components/generic/ClosableMessage'
import RouterViewLayout from '@/views/RouterViewLayout'
import Step from '@/components/generic/bulma/Step'

export default {
  name: 'Pipelines',
  components: {
    ClosableMessage,
    RouterViewLayout,
    Step
  },
  data() {
    return {
      steps: [
        {
          name: 'extractors',
          subView: 'extractorSettings',
          routeMatches: ['extractors', 'extractorSettings']
        },
        {
          name: 'entities',
          subView: 'extractorEntities',
          routeMatches: ['entities', 'extractorEntities']
        },
        {
          name: 'loaders',
          subView: 'loaderSettings',
          routeMatches: ['loaders', 'loaderSettings']
        },
        {
          name: 'schedules',
          subView: 'createSchedule',
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
    getIsStepEntitiesMinimallyValidated() {
      return (
        this.installedPlugins.extractors &&
        this.installedPlugins.extractors.length > 0
      )
    },
    getIsStepLoadersMinimallyValidated() {
      return this.getIsStepEntitiesMinimallyValidated
    },
    getIsStepScheduleMinimallyValidated() {
      return (
        this.getIsStepLoadersMinimallyValidated &&
        this.installedPlugins.loaders &&
        this.installedPlugins.loaders.length > 0
      )
    },
    getModalName() {
      return this.currentStep.subView
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
      <ClosableMessage title="Meltano Pipelines">
        <p>
          <span class="has-text-weight-bold">Meltano</span> streamlines the
          collection, analysis, and dashboarding of data.
        </p>
        <p>
          <span class="is-italic">You need to collect the data first</span>. Use
          the steps below to set up your data pipeline(s).
        </p>
      </ClosableMessage>

      <div class="steps is-small" id="steps-data-setup">
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
              Extractors
            </button>
            <p>Source Connectors</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('entities'),
            'is-completed': getIsStepEntitiesMinimallyValidated
          }"
        >
          <div class="step-marker">2</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation"
              :class="{ 'is-active': getIsActiveStep('entities') }"
              :disabled="!getIsStepEntitiesMinimallyValidated"
              @click="setStep('entities')"
            >
              Entities
            </button>
            <p>Source Selections</p>
          </div>
        </div>
        <div
          class="step-item"
          :class="{
            'is-active': getIsActiveStep('loaders'),
            'is-completed': getIsStepLoadersMinimallyValidated
          }"
        >
          <div class="step-marker">3</div>
          <div class="step-details">
            <button
              class="step-title button is-interactive-navigation"
              :class="{ 'is-active': getIsActiveStep('loaders') }"
              :disabled="!getIsStepLoadersMinimallyValidated"
              @click="setStep('loaders')"
            >
              Loaders
            </button>
            <p>Target Connectors</p>
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
              Schedules
            </button>
            <p>Data Pipelines</p>
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

<style lang="scss"></style>
