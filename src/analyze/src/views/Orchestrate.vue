<template>
  <router-view-layout>

    <div slot='left'>
      <nav class="menu">
        <div class="menu-label">Orchestrate</div>
        <ul class="menu-list">
          <li>
            <a @click="currentViewClicked('intro')"
              :class="{'is-active': isIntroView}">
              Intro
            </a>
            <a @click="currentViewClicked('extractor')"
              :class="{'is-active': isExtractorView}">
              Extract ({{currentExtractor || "unselected"}})
            </a>
          </li>
          <li>
            <a @click="currentViewClicked('loader')"
              :class="{'is-active': isLoaderView}">
              Load ({{currentLoader || "unselected"}})
            </a>
          </li>
          <li>
            <a @click="currentViewClicked('transform')"
              :class="{'is-active': isTransformView}">
              Transform ({{currentConnectionName || "unselected"}})
            </a>
          </li>
          <li>
            <a @click="currentViewClicked('run')"
              :class="{'is-active': isRunView,
                'disabled': !canRun}">
              Run!
            </a>
          </li>
        </ul>
      </nav>
    </div>

    <div slot="right">
      <div v-show="isIntroView">
        <h3 class="is-size-3">Introduction to Orchestrations</h3>
        <p>Here you will choose your extractor, loader and transformer.</p>
        <ol>
          <li>Your extractors are contained
            in the <code>extract</code> directory
            in the root of the installation.</li>
          <li>Your loaders are contained in the
            <code>load</code> directory in the
            root of the installation.</li>
          <li>Your transforms are contained in the
            <code>transform</code> directory in the
          root of the installation.</li>
        </ol>
        <p>You can see an example extractor, loader
          and transformer in their respective directories.</p>
        <p>On the left menu, select <code>extract</code>,
          and select from the list of available extractors.</p>
        <p>Do the same for the <code>load</code>.</p>
        <p>Once you have chosen an extractor and a loader, </p>
      </div>
      <div v-if="isExtractorView" key="extractorView">
        <h3 class="is-size-3">Extractors</h3>
        <p>Choose an extractor</p>
        <div class="select">
          <select @change="currentExtractorClicked">
            <option selected="true" disabled="disabled">Choose an extractor</option>
            <option v-for="extractor in extractors" :key="extractor">{{extractor}}</option>
          </select>
        </div>
      </div>
      <div v-else-if="isLoaderView" key="loaderView">
        <h3 class="is-size-3">Loaders</h3>
        <p>Choose a loader</p>
        <div class="select">
          <select @change="currentLoaderClicked">
            <option selected="true" disabled="disabled">Choose a loader</option>
            <option v-for="loader in loaders" :key="loader">{{loader}}</option>
          </select>
        </div>
      </div>
      <div v-else-if="isTransformView" key="transformView">
        <h3 class="is-size-3">Transformers</h3>
        <p>We'll use the transformer with the same name as the extractor.</p>
        <div class="select">
          <select @click="currentConnectionNameClicked">
            <option selected="true" disabled="disabled">Choose a connection</option>
            <option v-for="connection in connectionNames"
              :key="connection">{{connection}}</option>
          </select>
        </div>
      </div>
      <div v-else-if="isRunView" key="runView">
        <h3 class="is-size-3">Run Orchestration</h3>
        <p>This will run:</p>
        <ol>
          <li>Extractor: {{currentExtractor}}</li>
          <li>Loader: {{currentLoader}}</li>
          <li>Transformation: {{currentExtractor}}
            with {{currentConnectionName}} connection</li>
        </ol>
        <div class="log-output">{{log}}</div>
        <a @click="runJobs" class="button is-primary is-large">Run</a>
      </div>
    </div>

  </router-view-layout>
</template>
<script>
import { mapState, mapGetters, mapActions } from 'vuex';
import RouterViewLayout from '@/views/RouterViewLayout';

export default {
  name: 'Orchestrate',
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getConnectionNames');
  },
  components: {
    RouterViewLayout,
  },
  computed: {
    ...mapState('orchestrations', [
      'extractors',
      'loaders',
      'connectionNames',
      'currentConnectionName',
      'currentExtractor',
      'currentLoader',
      'log',
    ]),
    ...mapGetters('orchestrations', [
      'isIntroView',
      'isExtractorView',
      'isLoaderView',
      'isTransformView',
      'isRunView',
      'canRun',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'currentViewClicked',
      'currentConnectionNameClicked',
      'currentExtractorClicked',
      'currentLoaderClicked',
      'runJobs',
    ]),
  },

  beforeRouteUpdate(to, from, next) {
    this.$store.dispatch('orchestrations/getAll');
    next();
  },
};
</script>
