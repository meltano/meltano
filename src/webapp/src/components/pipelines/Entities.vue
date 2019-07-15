<script>
import { mapActions, mapGetters, mapState } from 'vuex';

import ConnectorLogo from '@/components/generic/ConnectorLogo';

export default {
  name: 'Entities',
  components: {
    ConnectorLogo,
  },
  created() {
    this.$store.dispatch('plugins/getAllPlugins');
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
      'plugins',
    ]),
  },
  methods: {
    ...mapActions('plugins', [
      'installPlugin',
    ]),
    installRequired(extractor) {
      this.installPlugin({ pluginType: 'extractors', name: extractor });
      this.$router.push({ name: 'extractorSettings', params: { extractor } });
    },
    udpateExtractorEntities(extractor) {
      this.$router.push({ name: 'extractorEntities', params: { extractor } });
    },
  },
};
</script>

<template>
  <div>

    <div class="columns">
      <div class="column is-three-fifths is-offset-one-fifth">
        <div class='content has-text-centered'>
          <p class='level-item buttons'>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Select all or a subset of the available data</span>
            </a>
            <span class='step-spacer'>then</span>
            <a class="button is-small is-static is-marginless is-borderless">
              <span>Save your selection</span>
            </a>
          </p>
        </div>
      </div>
    </div>

    <div class="tile is-ancestor is-flex is-flex-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(extractor, index) in plugins.extractors"
        :key="`${extractor}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <ConnectorLogo
              :connector='extractor'
              :is-grayscale='!getIsPluginInstalled("extractors", extractor)' />
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{extractor}}
            </p>

            <a
              v-if='getIsPluginInstalled("extractors", extractor)'
              class='button is-interactive-primary is-block is-small'
              @click="udpateExtractorEntities(extractor)">Edit Selections</a>
            <a
              v-else
              class='button is-interactive-primary is-outlined is-block is-small'
              @click="installRequired(extractor)">Install</a>

          </div>
        </div>
      </div>
    </div>

  </div>

</template>

<style lang="scss">
</style>
