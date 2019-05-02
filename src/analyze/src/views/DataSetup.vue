<script>
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'DataSetup',
  components: {
    RouterViewLayout,
  },
  data() {
    return {
      currentStep: {},
      steps: [
        { name: 'extractors', routeMatches: ['extractors', 'extractorSettings'] },
        { name: 'entities', routeMatches: ['entities', 'extractorEntities'] },
        { name: 'loaders', routeMatches: ['loaders', 'loaderSettings'] },
        { name: 'run', routeMatches: ['run'] },
      ],
      isModal: this.$route.meta.isModal,
    };
  },
  created() {
    this.updateStepFromRoute(this.$route.name);
  },
  beforeRouteUpdate(to, from, next) {
    this.updateStepFromRoute(to.name);
    this.updateModal(to.meta.isModal);
    next();
  },
  computed: {
    getIsActiveStep() {
      return stepName => this.currentStep.name === stepName;
    },
    getIsStepEntitiesMinimallyValidated() {
      return true; // TODO proper minimally validated validation
    },
    getIsStepLoadersMinimallyValidated() {
      return true; // TODO proper minimally validated validation
    },
    getIsStepRunMinimallyValidated() {
      return true; // TODO proper minimally validated validation
    },
  },
  methods: {
    setStep(stepName) {
      this.currentStep = this.steps.find(step => step.name === stepName);
      this.$router.push(this.currentStep);
    },
    updateModal(isModal) {
      this.isModal = isModal;
    },
    updateStepFromRoute(routeName) {
      const stepNameFromRoute = routeName;
      this.currentStep = this.steps
        .find(step => step.routeMatches.find(routeMatch => stepNameFromRoute === routeMatch));
    },
  },
};
</script>

<template>
  <router-view-layout>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class='content has-text-centered'>
          <p><span class='has-text-weight-bold'>Meltano</span> streamlines the collection and analysis of data.</p>
          <p><span class="is-italic">You need to collect the data first</span>. Use the steps below to do so.</p>
        </div>
      </div>
    </div>

    <div class="steps is-small" id="steps-data-setup">
      <div
        class="step-item is-completed"
        :class="{ 'is-active': getIsActiveStep('extractors') }">
        <div class="step-marker">1</div>
        <div class="step-details">
          <button
            class="step-title button is-interactive-navigation is-outlined"
            :class="{ 'is-active': getIsActiveStep('extractors') }"
            @click='setStep("extractors")'>Extractors</button>
          <p>Data Sources</p>
        </div>
      </div>
      <div
        class="step-item"
        :class="{
          'is-active': getIsActiveStep('entities'),
          'is-completed': getIsStepEntitiesMinimallyValidated
        }">
        <div class="step-marker">2</div>
        <div class="step-details">
          <button
            class="step-title button is-interactive-navigation is-outlined"
            :class="{ 'is-active': getIsActiveStep('entities') }"
            :disabled='!getIsStepEntitiesMinimallyValidated'
            @click='setStep("entities")'>Entities</button>
          <p>Source Selections</p>
        </div>
      </div>
      <div
        class="step-item"
        :class="{
          'is-active': getIsActiveStep('loaders'),
          'is-completed': getIsStepLoadersMinimallyValidated
        }">
        <div class="step-marker">3</div>
        <div class="step-details">
          <button
            class="step-title button is-interactive-navigation is-outlined"
            :class="{ 'is-active': getIsActiveStep('loaders') }"
            :disabled='!getIsStepLoadersMinimallyValidated'
            @click='setStep("loaders")'>Loaders</button>
          <p>Selection Targets</p>
        </div>
      </div>
      <div
        class="step-item"
        :class="{
          'is-active': getIsActiveStep('run'),
          'is-completed': getIsStepRunMinimallyValidated
        }">
        <div class="step-marker">4</div>
        <div class="step-details">
          <button
            class="step-title button is-interactive-navigation is-outlined"
            :class="{ 'is-active': getIsActiveStep('run') }"
            :disabled='!getIsStepRunMinimallyValidated'
            @click='setStep("run")'>Run</button>
          <p>Get Data</p>
        </div>
      </div>

      <div class="steps-content">
        <div
          class="step-content"
          :class="{ 'is-active': getIsActiveStep('extractors') }">
          <router-view></router-view>
          <div v-if='isModal'>
            <router-view name='extractorSettings'></router-view>
          </div>
        </div>
        <div
          class="step-content"
          :class="{ 'is-active': getIsActiveStep('entities') }">
          <router-view></router-view>
          <div v-if='isModal'>
            <router-view name='extractorEntities'></router-view>
          </div>
        </div>
        <div
          class="step-content"
          :class="{ 'is-active': getIsActiveStep('loaders') }">
          <router-view></router-view>
          <div v-if='isModal'>
            <router-view name='loaderSettings'></router-view>
          </div>
        </div>
        <div
          class="step-content"
          :class="{ 'is-active': getIsActiveStep('run') }">
          <router-view></router-view>
        </div>
      </div>

    </div>

  </router-view-layout>
</template>

<style lang="scss">
</style>
