<script>
import { mapActions, mapGetters, mapState } from 'vuex';

export default {
  name: 'Extractors',
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapGetters('orchestrations', [
      'getExtractorImageUrl',
      'getExtractorNameWithoutPrefixedTapDash',
      'getIsExtractorPluginInstalled',
      'getIsInstallingExtractorPlugin',
    ]),
    ...mapState('orchestrations', [
      'installedPlugins',
      'extractors',
    ]),
  },
  methods: {
    ...mapActions('orchestrations', [
      'installExtractor',
    ]),
    installExtractorAndBeginSettings(extractor) {
      this.installExtractor(extractor);
      this.updateExtractorSettings(extractor);
    },
    updateExtractorSettings(extractor) {
      this.$router.push({ name: 'extractorSettings', params: { extractor } });
    },
  },
};
</script>

<template>
  <div>

    <div class="tile is-ancestor flex-and-wrap">
      <div
        class="tile is-parent is-3"
        v-for="(extractor, index) in extractors"
        :key="`${extractor}-${index}`">
        <div class="tile level is-child box">
          <div class="image level-item is-64x64 container">
            <img
              :class='{ "grayscale": !getIsExtractorPluginInstalled(extractor) }'
              :src='getExtractorImageUrl(extractor)'
              :alt="`${getExtractorNameWithoutPrefixedTapDash(extractor)} logo`">
          </div>
          <div class="content is-small">
            <p class='has-text-centered'>
              {{extractor}}
            </p>

            <template v-if='getIsExtractorPluginInstalled(extractor)'>
              <div class="buttons are-small">
                <a
                  class='button is-interactive-primary flex-grow-1'
                  @click="updateExtractorSettings(extractor)">Account Settings</a>
                <a class='button' disabled>Uninstall</a>
              </div>
            </template>
            <template v-else>
              <a
                :class='{ "is-loading": getIsInstallingExtractorPlugin(extractor) }'
                class='button is-interactive-primary is-outlined is-block is-small'
                @click="installExtractorAndBeginSettings(extractor)">Install</a>
            </template>

          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
