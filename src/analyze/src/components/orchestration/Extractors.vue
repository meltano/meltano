<script>
import { mapActions, mapGetters, mapState } from 'vuex';

export default {
  name: 'Extractors',
  data() {
    return {
      filterExtractorsText: '',
    };
  },
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
    filteredExtractors() {
      if (this.filterExtractorsText) {
        return this.extractors
          .filter(item => item.indexOf(this.filterExtractorsText) > -1);
      }
      return this.extractors;
    },
  },
  methods: {
    ...mapActions('orchestrations', [
      'installExtractor',
    ]),
    updateExtractorSettings(extractor) {
      this.$router.push({ name: 'extractorSettings', params: { extractor } });
    },
  },
};
</script>

<template>
  <div>

    <div
      v-if="filteredExtractors.length === 0"
      class='content'>
      <p>
        No extractors are available.
      </p>
    </div>

    <template v-else>
      <div class="columns">
        <div class="column is-4 is-offset-4">
          <input
            type="text"
            v-model="filterExtractorsText"
            placeholder="Filter extractors..."
            class="input connector-input">
        </div>
      </div>

      <div class="tile is-ancestor flex-and-wrap">
        <div
          class="tile is-parent is-3"
          v-for="(extractor, index) in filteredExtractors"
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
                  @click="installExtractor(extractor)">Install</a>
              </template>

            </div>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<style lang="scss">
.flex-grow-1 {
  flex-grow: 1;
}
</style>
