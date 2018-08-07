<template>
  <div class="container">
    <section class="section">
      <div class="columns">
        <nav class="column is-one-quarter menu">
          <div class="menu-label">Orchestrate</div>
          <ul class="menu-list">
            <li>
              <a @click="currentViewClicked('extractor')"
                :class="{'is-active': isExtractorView}">
                Extract ({{currentExtractor}})
              </a>
            </li>
            <li>
              <a @click="currentViewClicked('loader')"
                :class="{'is-active': isLoaderView}">
                Load ({{currentLoader}})
              </a>
            </li>
            <li>
              <a @click="currentViewClicked('transform')"
                :class="{'is-active': isTransformView}">
                Transform ({{currentExtractor}})
              </a>
            </li>
            <li>
              <a @click="currentViewClicked('run')"
                :class="{'disabled': !canRun}">
                Run!
              </a>
            </li>
          </ul>
        </nav>
        <div class="column">
          <div v-if="isExtractorView">
            <h3 class="is-size-3">Extractors</h3>
            <p>Choose an extractor</p>
            <div class="select">
              <select @change="currentExtractorClicked">
                <option selected="true" disabled="disabled">Choose an extractor</option>
                <option v-for="extractor in extractors" :key="extractor">{{extractor}}</option>
              </select>
            </div>
          </div>
          <div v-else-if="isLoaderView">
            <h3 class="is-size-3">Loaders</h3>
            <p>Choose a loader</p>
            <div class="select">
              <select @change="currentLoaderClicked">
                <option selected="true" disabled="disabled">Choose a loader</option>
                <option v-for="loader in loaders" :key="loader">{{loader}}</option>
              </select>
            </div>
          </div>
          <div v-else-if="isTransformView">
            <h3 class="is-size-3">Transformers</h3>
            <p>We'll use the transformer with the same name as the extractor.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';

export default {
  name: 'Orchestrate',
  computed: {
    ...mapState('orchestrations', [
      'extractors',
      'loaders',
      'currentExtractor',
      'currentLoader',
    ]),
    ...mapGetters('orchestrations', [
      'isExtractorView',
      'isLoaderView',
      'isTransformView',
      'canRun',
    ]),
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
  },

  methods: {
    ...mapActions('orchestrations', [
      'currentViewClicked',
      'currentExtractorClicked',
      'currentLoaderClicked',
    ]),
  },

  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
