<script>
import { mapState } from 'vuex';

import EntitiesSelector from '@/components/orchestration/EntitiesSelector';

export default {
  name: 'Entities',
  components: {
    EntitiesSelector,
  },
  data() {
    return {
      filterExtractorsText: '',
      installingExtractors: [],
      extractorInFocus: null,
    };
  },
  created() {
    this.$store.dispatch('orchestrations/getAll');
    this.$store.dispatch('orchestrations/getInstalledPlugins');
  },
  computed: {
    ...mapState('orchestrations', [
      'installedPlugins',
      'extractors',
    ]),
    getImageUrl() {
      return extractor => `/static/logos/${this.getNameWithoutPrefixedTapDash(extractor)}-logo.png`;
    },
    getNameWithoutPrefixedTapDash() {
      return extractor => extractor.replace('tap-', '');
    },
    filteredExtractors() {
      // Alphabetize filter (TODO: temp until getInstalledPlugins is alphabetical like getAll)
      const alphabetized = this.extractors.filter(
        extractor => this.installedPlugins.extractors.find(item => item.name === extractor));

      // Input filter
      if (this.filterExtractorsText) {
        return alphabetized.filter(item => item.indexOf(this.filterExtractorsText) > -1);
      }
      return alphabetized;
    },
  },
  methods: {
    updateExtractorInFocus(extractor) {
      const extractorObj = this.installedPlugins.extractors.find(item => item.name === extractor);
      this.extractorInFocus = extractorObj;
    },
  },
};
</script>

<template>
  <div>
    <div v-if='extractorInFocus'>

      <EntitiesSelector
        :extractor='extractorInFocus'
        :imageUrl='getImageUrl(extractorInFocus.name)'
        @clearExtractorInFocus='updateExtractorInFocus(null)'>
      </EntitiesSelector>

    </div>

    <div v-else>

      <div class="columns">
        <div class="column is-4 is-offset-4">
          <input
            type="text"
            v-model="filterExtractorsText"
            placeholder="Filter installed extractors..."
            class="input connector-input">
        </div>
      </div>

      <div class="tile is-ancestor flex-and-wrap">
        <div
          class="tile is-parent is-3"
          v-for="(extractor, index) in filteredExtractors"
          :key="`${extractor}-${index}`">
          <div class="tile is-child box">
            <div class="image is-64x64 container">
              <img
                :src='getImageUrl(extractor)'
                :alt="`${getNameWithoutPrefixedTapDash(extractor)} logo`">
            </div>
            <div class="content is-small">
              <p class='has-text-centered'>
                {{extractor}}
              </p>

              <a
                class='button is-success is-outlined is-block is-small'
                @click="updateExtractorInFocus(extractor)">Edit Selections</a>

            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style lang="scss">
</style>
