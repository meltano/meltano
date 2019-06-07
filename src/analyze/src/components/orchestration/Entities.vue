<script>
import { mapGetters, mapState } from 'vuex';

export default {
  name: 'Entities',
  created() {
    this.$store.dispatch('plugins/getAllPlugins');
    this.$store.dispatch('plugins/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('configuration', [
      'getExtractorImageUrl',
      'getExtractorNameWithoutPrefixedTapDash',
    ]),
    ...mapGetters('plugins', [
      'getIsPluginInstalled',
    ]),
    ...mapState('plugins', [
      'installedPlugins',
      'plugins',
    ]),
  },
  methods: {
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

    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(extractor, index) in plugins.extractors"
        :key="`${extractor}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <img
              :class='{ "grayscale": !getIsPluginInstalled("extractors", extractor) }'
              :src='getExtractorImageUrl(extractor)'
              :alt="`${getExtractorNameWithoutPrefixedTapDash(extractor)} logo`">
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{extractor}}
            </p>

            <a
              class='button is-interactive-primary is-outlined is-block is-small'
              @click="udpateExtractorEntities(extractor)">Edit Selections</a>
          </div>
        </div>
      </div>
    </div>

  </div>

</template>

<style lang="scss">
</style>
