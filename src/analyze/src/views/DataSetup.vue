<script>
import Entities from '@/components/orchestration/Entities';
import Extractors from '@/components/orchestration/Extractors';
import Loaders from '@/components/orchestration/Loaders';
import RouterViewLayout from '@/views/RouterViewLayout';
import RunSummary from '@/components/orchestration/RunSummary';

import bulmaSteps from '@/../node_modules/bulma-steps/dist/js/bulma-steps';

export default {
  name: 'DataSetup',
  components: {
    Entities,
    Extractors,
    Loaders,
    RouterViewLayout,
    RunSummary,
  },
  mounted() {
    bulmaSteps.attach();
  },
};
</script>

<template>
  <router-view-layout>

    <div class="steps is-small" id="steps-data-setup">
      <div class="step-item is-active">
        <div class="step-marker">1</div>
        <div class="step-details">
          <p class="step-title">Extractors</p>
          <p>Data Sources</p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-marker">2</div>
        <div class="step-details">
          <p class="step-title">Entities</p>
          <p>Source Selections</p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-marker">3</div>
        <div class="step-details">
          <p class="step-title">Loaders</p>
          <p>Selection Targets</p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-marker">4</div>
        <div class="step-details">
          <p class="step-title">Run</p>
          <p>Get Data</p>
        </div>
      </div>

      <div class="steps-actions">
        <div class="steps-action">
          <a href="#" data-nav="previous" class="button is-light">Previous</a>
        </div>
        <div class="steps-action">
          <a href="#" data-nav="next" class="button is-light">Next</a>
        </div>
      </div>

      <div class="steps-content">
        <div class="step-content is-active">
          <Extractors></Extractors>
        </div>
        <div class="step-content">
          <Entities></Entities>
        </div>
        <div class="step-content">
          <Loaders></Loaders>
        </div>
        <div class="step-content">
          <RunSummary></RunSummary>
        </div>
      </div>
    </div>

  </router-view-layout>
</template>

<style lang="scss">
</style>
